# `profile_and_register_table`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview reference-lifecycle-chip-prominent">Preview</span>
<span class="reference-chip reference-chip-muted">Public function</span>
</p>

> This function is available for evaluation but is not part of the supported Live release contract. It may change without backward-compatibility guarantees.

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

`fabricops_kit/pipeline/profile_and_register_table.py:466`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline/profile_and_register_table.py#L466-L817">View on GitHub</a>
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
| `profile_role` | `{"source", "target"}` | Yes | Records whether the profiled asset participated in the notebook activity as an input or an output: ``source`` for an activity input and ``target`` for an activity output. The value is stored in ``METADATA_DATA_LINEAGE`` rather than in ``METADATA_DATA_PROFILED`` or ``METADATA_DATA_CATALOGUE``. |
| `target` | `str` | Yes | Configured FabricStore target key. Its normalized key becomes the physical identity's layer and its store kind determines whether the asset is a Lakehouse or Warehouse table. |
| `table_name` | `str` | Yes | Physical table name of the business asset being profiled. This identifies the asset and does not redirect metadata writes. |
| `schema` | `str` | No | Physical schema name, or ``None`` to use the configured store default. Classic or schema-disabled Lakehouses preserve ``None``. |
| `frequency_columns` | `sequence of str` | No | Selected columns whose flattened frequency rows should be persisted. ``None`` profiles eligible non-technical scalar columns. An empty sequence skips frequency profiling entirely and writes no child rows. Requested columns should also be eligible for the main statistical profile. |
| `frequency_top_n` | `int \| None` | No | Optional number of ranked values to retain per selected frequency column. ``None`` retains every distinct value. |
| `frequency_max_distinct_percent` | `float \| None` | No | Automatic frequency-profiling safeguard used only when ``frequency_columns=None``. Columns whose distinct-per-non-null percentage is greater than this threshold are skipped and produce no child frequency rows. Values must be between ``0.0`` and ``100.0`` when supplied. ``None`` disables the high-cardinality threshold; all-null automatic columns remain skipped. Explicit ``frequency_columns`` selections override this threshold. |
| `frequency_profile_df` | `pyspark.sql.DataFrame` | No | Optional caller-provided Spark DataFrame to use only for frequency distribution calculation. ``None`` preserves full-source frequency profiling. When supplied, it must contain every selected frequency column, may contain extra columns, and must use a compatible Spark session when this can be determined. The caller is responsible for preparing, persisting, refreshing, and governing this DataFrame; this function does not verify whether it is random, representative, sampled, persisted, or otherwise suitable for the caller's purpose. |

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
3. Call ``profile_frequency_distribution`` to produce flattened frequency
   rows for the selected columns.
4. Resolve each frequency row to its parent ``metadata_column_key`` and
   prepare it with the same ``profiled_at`` snapshot timestamp.
5. Save the compact profiling snapshot to ``METADATA_DATA_PROFILED``.
6. Replace rows for the exact ``metadata_column_key + profiled_at`` child
   snapshot and write the normalized rows to
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
- Historical parent and child snapshots join on both
  ``metadata_column_key`` and ``profiled_at``. Rows are replaced only for
  that exact snapshot identity, so earlier snapshots remain intact.

``METADATA_DATA_PROFILED`` receives one appended row per eligible input
DataFrame column. Repeated executions create additional profiling
snapshots, and the returned DataFrame is the same compact DataFrame
appended to this table. Its logical field groups are:

- Identity fields: ``metadata_table_key``, ``metadata_column_key``,
  ``environment_name``, ``store_type``, ``layer``, ``schema_name``,
  ``table_name``, ``column_name``, ``data_type``.
- Statistical fields: ``row_count``, ``non_null_count``, ``null_count``,
  ``null_percent``, ``distinct_count``, ``distinct_percent``,
  ``mean_value``, ``stddev_value``, ``min_value``,
  ``percentile_25_value``, ``median_value``, ``percentile_75_value``,
  ``max_value``.
- Runtime fields: ``schema_fingerprint``, ``profiled_at``.
- Audit fields: ``_committed_by``, ``_committed_at``, ``_workspace_id``,
  ``_workspace_name``, ``_notebook_id``, ``_notebook_name``,
  ``_metadata_lakehouse_name``, ``_activity_id``.

``METADATA_DATA_PROFILED`` saves a new compact profiling snapshot. One row
is saved for each eligible DataFrame column. ``METADATA_DATA_PROFILED_FREQUENCY``
saves one flattened row per returned distinct value. Earlier parent and
child snapshots are retained and join on ``metadata_column_key + profiled_at``.

``METADATA_DATA_CATALOGUE`` stores table and column records, not profiling
measurements. FabricOps creates a stable ID for the table and each column,
then checks whether the same table, column, and schema already exist. If a
matching record exists, it is updated. Otherwise, a new record is added.
Matching uses ``environment_name + metadata_table_key +
metadata_column_key + schema_fingerprint``:

- ``metadata_table_key``: stable logical table identity shared across
  environments.
- ``metadata_column_key``: stable logical column identity shared across
  environments.
- ``schema_fingerprint``: deterministic fingerprint of ordered schema
  content, independent of deployment environment. The current schema
  contract includes ordered column names and data types; nullability is
  not currently part of the fingerprint.
- ``environment_name``: environment-specific catalogue observation.

One logical Data Contract link can therefore govern the same dataset in
Development and Production, while catalogue and execution observations
remain separate and promotion checks can compare matching logical keys.
Existing metadata created with environment-coupled identities must be
recreated or explicitly migrated; FabricOps does not provide a legacy-key
compatibility path.

A changed ``schema_fingerprint`` represents a newly observed table
structure and can create a new catalogue snapshot.

``METADATA_DATA_LINEAGE`` records whether the table was used as an input
or produced as an output during the current notebook activity. A
``profile_role="source"`` value means the DataFrame was used as an input.
A ``profile_role="target"`` value means the DataFrame was produced as an
output. Lineage-specific fields are ``lineage_event_id``,
``metadata_table_key``, ``schema_fingerprint``, ``profile_role``,
``profiled_at``, and ``environment_name``. The standard eight underscore
audit fields are the sole execution-context contract. ``profiled_at`` is
the dataset profile snapshot time, while ``_committed_at`` is the metadata
write time. ``lineage_event_id`` is deterministically derived from
``_activity_id``, ``metadata_table_key``, ``schema_fingerprint``, and
``profile_role``.

What the notebook receives: a Spark DataFrame containing one profiling
result row for each eligible column.

What FabricOps saves:

- ``METADATA_DATA_PROFILED``: a new compact profiling snapshot.
- ``METADATA_DATA_PROFILED_FREQUENCY``: flattened frequency rows linked by
  ``metadata_column_key`` and ``profiled_at``.
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

Removing ``frequency_json`` from ``METADATA_DATA_PROFILED`` and adding the
normalized child table is a breaking physical-schema change. Existing
metadata tables may need recreation through the established setup flow;
no compatibility or automatic migration layer is provided.

</div>

## See also

- [Pipeline Execution](../../guided-demo/02-run-pipeline.md)


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

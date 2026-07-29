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

`fabricops_kit/pipeline/profile_and_register_table.py:538`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline/profile_and_register_table.py#L538-L870">View on GitHub</a>
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
| `frequency_columns` | `sequence of str` | No | Selected columns that should receive embedded frequency evidence. ``None`` profiles all eligible non-technical scalar columns. An empty sequence skips frequency profiling entirely and persists null ``frequency_json`` for every statistical profile row. Requested columns should also be eligible for the main statistical profile. |
| `frequency_top_n` | `int \| None` | No | Optional number of ranked values to retain per selected frequency column. ``None`` retains every distinct value. |
| `frequency_max_distinct_percent` | `float \| None` | No | Automatic frequency-profiling safeguard used only when ``frequency_columns=None``. Columns whose distinct-per-non-null percentage is greater than this threshold receive structured skipped JSON instead of generated frequencies. Values must be between ``0.0`` and ``100.0`` when supplied. ``None`` disables the high-cardinality threshold; all-null automatic columns still receive structured skipped JSON. Explicit ``frequency_columns`` selections override this threshold. |
| `frequency_profile_df` | `pyspark.sql.DataFrame` | No | Optional caller-provided Spark DataFrame to use only for frequency distribution calculation. ``None`` preserves full-source frequency profiling. When supplied, it must contain every selected frequency column, may contain extra columns, and must use a compatible Spark session when this can be determined. The caller is responsible for preparing, persisting, refreshing, and governing this DataFrame; this function does not verify whether it is random, representative, sampled, persisted, or otherwise suitable for the caller's purpose. |

## Returns

Spark DataFrame containing one detailed profiling row for each eligible column appended to METADATA_DATA_PROFILED, including stable table and column IDs, complete-DataFrame statistical metrics, frequency_json where enabled, schema fingerprint, and runtime audit fields.

### Return interpretation

The returned rows are the detailed profile results for eligible columns. Statistical metrics always describe the complete supplied DataFrame. Frequency counts and percentages describe the complete source by default or the caller-provided frequency_profile_df when supplied; frequency_json discloses source_row_count, profiled_row_count, profiled_non_null_count, and frequency_scope. Catalogue rows and source or target activity records are saved as side effects and are not returned.

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
   columns receive structured skipped JSON, and all-null columns receive
   structured no-non-null-values skipped JSON. Explicit non-empty
   ``frequency_columns`` bypass this threshold, while
   ``frequency_columns=[]`` skips frequency profiling entirely.
3. Convert the multiple frequency rows for each column into one
   deterministic JSON document.
4. Left-join that JSON to the statistical profile on
   ``profile_dataframe.COLUMN_NAME = profile_frequency_distribution.COLUMN_NAME``.
5. Save a new profiling snapshot to ``METADATA_DATA_PROFILED``.
6. Create stable table and column IDs, then update matching catalogue
   records or add new records in ``METADATA_DATA_CATALOGUE``.
7. Record whether the table was used as an input or produced as an output
   in ``METADATA_DATA_LINEAGE``.
8. Return the detailed Spark DataFrame written to
   ``METADATA_DATA_PROFILED``.

User-facing workflow:

Supplied DataFrame
    ↓
Calculate column statistics and value frequencies
    ↓
Save a new profiling snapshot
``METADATA_DATA_PROFILED``
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

Frequency join behavior:

- The statistical profile is the left side of the join, so every eligible
  statistical profile row remains in the returned result.
- ``frequency_columns=None`` automatically profiles eligible non-technical
  scalar columns whose distinct-per-non-null percentage is less than or
  equal to ``frequency_max_distinct_percent``. The default threshold is
  ``80.0`` percent.
- Automatically selected columns above the threshold receive deterministic
  structured ``frequency_json`` with ``status="skipped"`` and
  ``reason="high_cardinality"``. All-null automatic columns receive
  ``reason="no_non_null_values"``.
- ``frequency_max_distinct_percent=None`` disables the high-cardinality
  threshold for automatic columns.
- Only columns listed in a non-empty ``frequency_columns`` sequence receive
  generated frequency evidence; explicit selections override the automatic
  threshold. Other profiled columns receive null.
- ``frequency_columns=[]`` skips frequency profiling entirely and persists
  null ``frequency_json`` for every row.
- ``frequency_profile_df=None`` profiles frequencies against the complete
  supplied source DataFrame. When a caller supplies ``frequency_profile_df``,
  frequency counts, percentages, ranks, profiled row counts, and profiled
  non-null counts describe that caller-provided DataFrame, while
  ``source_row_count`` records the complete source DataFrame row count.
- ``frequency_top_n`` restricts embedded values only when supplied. It
  limits output rows after grouped counts are calculated and does not
  reduce grouping cost.
- Frequency values are ordered deterministically by rank.

Example ``frequency_json`` structure:

.. code-block:: json

   {
     "source_row_count": 1000,
     "profiled_row_count": 1000,
     "profiled_non_null_count": 995,
     "frequency_scope": "full_source",
     "values": [
       {
         "value": "Active",
         "count": 700,
         "percent": 70.0,
         "rank": 1
       }
     ]
   }

``METADATA_DATA_PROFILED`` receives one appended row per eligible input
DataFrame column. Repeated executions create additional profiling
snapshots, and the returned DataFrame is the same detailed DataFrame
appended to this table. Its logical field groups are:

- Identity fields: ``metadata_table_key``, ``metadata_column_key``,
  ``environment_name``, ``store_type``, ``layer``, ``schema_name``,
  ``table_name``, ``column_name``, ``data_type``.
- Statistical fields: ``row_count``, ``non_null_count``, ``null_count``,
  ``null_percent``, ``distinct_count``, ``distinct_percent``,
  ``mean_value``, ``stddev_value``, ``min_value``,
  ``percentile_25_value``, ``median_value``, ``percentile_75_value``,
  ``max_value``.
- Frequency and runtime fields: ``frequency_json``, ``schema_fingerprint``,
  ``profiled_at``.
- Audit fields: ``_committed_by``, ``_committed_at``, ``_workspace_id``,
  ``_workspace_name``, ``_notebook_id``, ``_notebook_name``,
  ``_metadata_lakehouse_name``, ``_activity_id``.

``METADATA_DATA_PROFILED`` saves a new profiling snapshot. One row is
saved for each eligible DataFrame column. Earlier profiling snapshots are
retained.

``METADATA_DATA_CATALOGUE`` stores table and column records, not profiling
measurements. FabricOps creates a stable ID for the table and each column,
then checks whether the same table, column, and schema already exist. If a
matching record exists, it is updated. Otherwise, a new record is added.
Matching uses ``metadata_table_key + metadata_column_key +
schema_fingerprint``:

- ``metadata_table_key``: stable ID for the table.
- ``metadata_column_key``: stable ID for a column within that table.
- ``schema_fingerprint``: identifier for the DataFrame structure observed
  during profiling.

A changed ``schema_fingerprint`` represents a newly observed table
structure and can create a new catalogue snapshot.

``METADATA_DATA_LINEAGE`` records whether the table was used as an input
or produced as an output during the current notebook activity. A
``profile_role="source"`` value means the DataFrame was used as an input.
A ``profile_role="target"`` value means the DataFrame was produced as an
output. Key lineage fields include ``lineage_event_id``,
``activity_id``, ``notebook_id``, ``notebook_name``, ``workspace_id``,
``workspace_name``, ``metadata_table_key``, ``schema_fingerprint``,
``profile_role``, ``profiled_at``, ``committed_by``,
``environment_name``, ``metadata_lakehouse_name``, and the standard audit
fields. ``lineage_event_id`` is deterministically derived from
``activity_id``, ``metadata_table_key``, ``schema_fingerprint``, and
``profile_role``.

What the notebook receives: a Spark DataFrame containing one profiling
result row for each eligible column.

What FabricOps saves:

- ``METADATA_DATA_PROFILED``: a new profiling snapshot.
- ``METADATA_DATA_CATALOGUE``: updated or newly added table and column
  records.
- ``METADATA_DATA_LINEAGE``: the current source or target activity.

Statistical profiling records describe the complete DataFrame supplied
during the notebook activity. If ``frequency_profile_df`` is supplied,
only generated frequency evidence uses that DataFrame and its JSON records
``frequency_scope="caller_provided"``. The function does not claim or
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

</div>

## See also

- [Pipeline Execution](../../guided-demo/run-pipeline.md)


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

<!-- Generated file. Edit docs/releases/manifests/0.2.0.yml or the authoritative source metadata and regenerate. -->

# `profile_table`

<span class="fabricops-release-status fabricops-release-status--live">Live</span>

Package version: `0.2.0`

Qualified callable: `fabricops_kit.pipeline.profile_table.profile_table`

Source path: `src/fabricops_kit/pipeline/profile_table.py`

Frozen source ref: `v0.2.0`

[View frozen source](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/v0.2.0/src/fabricops_kit/pipeline/profile_table.py)

Signature: `profile_table(*, dataframe=None, store: 'str | None' = None, schema: 'str | None' = None, table_name: 'str | None' = None, table_id: 'str | None' = None, frequency_columns=None, frequency_top_n: 'int | None' = None, frequency_max_distinct_percent: 'float | None' = 80.0, spark_session=None)`

## Description

Profile a Spark DataFrame or a complete governed physical table.

## Parameters

dataframe : pyspark.sql.DataFrame, optional
    Exact Spark DataFrame to profile. If a governed identity is also
    supplied, FabricOps does not re-read the physical table.
store : str, optional
    Configured physical store key. Supply with ``table_name`` and optional
    ``schema`` instead of ``table_id``.
schema : str, optional
    Physical schema when the configured store uses schemas.
table_name : str, optional
    Physical table name. Required with ``store`` when ``table_id`` is
    omitted.
table_id : str, optional
    Canonical governed table identity, mutually exclusive with physical
    coordinates.
frequency_columns : sequence of str, optional
    Columns to frequency profile. ``None`` automatically selects eligible
    scalar columns; an empty sequence skips frequency profiling.
frequency_top_n : int or None, optional
    Ranked values to retain per frequency column. ``None`` retains all.
frequency_max_distinct_percent : float or None, default=80.0
    Maximum distinct-per-non-null percentage for automatically selected
    columns. ``None`` disables the cardinality filter.
spark_session : object, optional
    Spark session to use. When omitted, FabricOps uses the supplied
    DataFrame session or resolves the active session.

## Return value

dict
    ``profile`` contains the canonical statistical Spark DataFrame and
    ``frequency_profile`` contains the applicable canonical frequency
    Spark DataFrame, or ``None`` when no columns were selected. Governed
    ``profile`` rows additionally contain persisted snapshot identities
    and audit fields.

## Usage notes

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

[Back to release overview](../index.md)

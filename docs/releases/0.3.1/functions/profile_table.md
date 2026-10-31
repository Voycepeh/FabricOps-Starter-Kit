<!-- Generated file. Edit docs/releases/manifests/0.3.1.yml or the authoritative source metadata and regenerate. -->

# `profile_table`

<span class="fabricops-release-status fabricops-release-status--live">Live</span>

Package version: `0.3.1`

Qualified callable: `fabricops_kit.pipeline.profile_table.profile_table`

Source path: `src/fabricops_kit/pipeline/profile_table.py`

Frozen source ref: `v0.3.1`

[View frozen source](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/v0.3.1/src/fabricops_kit/pipeline/profile_table.py)

Signature: `profile_table(*, dataframe=None, store: 'str | None' = None, schema: 'str | None' = None, table_name: 'str | None' = None, table_id: 'str | None' = None, grain_discovery_enabled: 'bool' = True, grain_discovery_max_columns: 'int' = 3, grain_discovery_max_candidates: 'int' = 8, frequency_columns=None, frequency_enabled: 'bool' = True, frequency_top_n: 'int | None' = 5, frequency_max_distinct_percent: 'float | None' = 80.0, context=None, verbose: 'bool' = True)`

## Description

Profile a Spark DataFrame or a complete governed physical table.

## Parameters

dataframe : pyspark.sql.DataFrame, optional
    Required unless a complete governed identity is provided. With no
    DataFrame and no identity, the call raises ValueError. If an identity is also
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
grain_discovery_enabled : bool, default=True
    Whether to discover candidate Grain keys for a governed table. False
    skips discovery queries and preserves saved Catalogue candidates.
    The caller controls when to enable discovery; no scheduling is applied.
    This option does not disable contract Grain checks. DataFrame-only
    profiling does not discover or persist candidates.
grain_discovery_max_columns : int, default=3
    Maximum columns in a candidate key. 1 checks single columns only; 2
    also checks pairs. Must be a positive integer. Wider searches can be costly.
grain_discovery_max_candidates : int, default=8
    Maximum candidate keys to retain at the smallest valid key width.
    Must be a positive integer. Discovery stops after enough keys are found;
    this limit does not cap work when no valid key exists.
frequency_columns : sequence of str, optional
    Columns to frequency profile. ``None`` automatically selects eligible
    scalar columns; an empty sequence skips frequency profiling.
frequency_enabled : bool, default=True
    Whether to calculate frequency distributions for this call. False skips all
    frequency columns. The caller controls when to enable frequency profiling.
frequency_top_n : int or None, default=5
    Ranked values to retain per frequency column. ``None`` retains all.
frequency_max_distinct_percent : float or None, default=80.0
    Maximum distinct-per-non-null percentage for automatically selected
    columns. ``None`` disables the cardinality filter.
context : dict, optional
    Explicit pipeline context; Testing returns profiles without persistence.
verbose : bool, optional
    Display profiling progress when True; orchestration uses the automatic report.

## Return value

dict
    ``profile`` contains the canonical statistical Spark DataFrame and
    ``frequency_profile`` contains the applicable canonical frequency
    Spark DataFrame, or ``None`` when no columns were selected. Governed
    ``profile`` rows additionally contain persisted snapshot identities
    and audit fields.

## Usage notes

The result also includes ``row_count``, reused from an existing aggregate
when available (None otherwise). No additional Spark job is run for this
metric. It describes the profiled dataset, not rows committed by a writer.

[Back to release overview](../index.md)

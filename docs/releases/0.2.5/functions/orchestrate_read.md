<!-- Generated file. Edit docs/releases/manifests/0.2.5.yml or the authoritative source metadata and regenerate. -->

# `orchestrate_read`

<span class="fabricops-release-status fabricops-release-status--live">Live</span>

Package version: `0.2.5`

Qualified callable: `fabricops_kit.pipeline.orchestrate_read.orchestrate_read`

Source path: `src/fabricops_kit/pipeline/orchestrate_read.py`

Frozen source ref: `v0.2.5`

[View frozen source](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/v0.2.5/src/fabricops_kit/pipeline/orchestrate_read.py)

Signature: `orchestrate_read(*, store: 'str', schema: 'str | None', table_name: 'str', read_mode: 'str' = 'full', query: 'str | None' = None, read_parameters: 'dict[str, Any] | None' = None, target_table_id: 'str | None' = None, frequency_enabled: 'bool' = True, frequency_top_n: 'int | None' = 5, spark_session=None, verbose: 'bool' = True) -> 'dict[str, Any]'`

## Description

Execute the standard FabricOps governed Read lifecycle.

## Parameters

store : str
    Configured source store key.
schema : str, optional
    Physical source schema.
table_name : str
    Physical source table name.
read_mode : {"full", "incremental"}, default="full"
    Source read behaviour forwarded to :func:`pipeline_read`.
query : str, optional
    Read-only Warehouse query forwarded to :func:`pipeline_read`.
read_parameters : dict, optional
    Incremental configuration, for example {"watermark_column": "modified_datetime"}.
    A selected Data Contract must agree with the supplied watermark.
target_table_id : str, optional
    Governed target identity required for incremental reads.
frequency_enabled : bool, default=True
    Whether to calculate frequency distributions for this table.
frequency_top_n : int or None, default=5
    Maximum ranked frequency values per eligible column; None retains all.
spark_session : object, optional
    Spark session used by every stage.
verbose : bool, default=True
    Print stage start, outcome, duration, and failure attribution.

## Return value

dict
    The ``pipeline_read`` result, including ``dataframe`` and ``table_id``,
    plus capability results and ``orchestration_stages``.

## Usage notes

Stages run as Read, Freshness, Schema, Data Quality, and Profile, matching
canonical ``02_pipeline``. Skipped capability results remain skipped.
DataFrames are never displayed. Incremental batches are not profiled.

[Back to release overview](../index.md)

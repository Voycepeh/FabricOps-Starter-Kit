<!-- Generated file. Edit docs/releases/manifests/0.2.5.yml or the authoritative source metadata and regenerate. -->

# `orchestrate_write`

<span class="fabricops-release-status fabricops-release-status--live">Live</span>

Package version: `0.2.5`

Qualified callable: `fabricops_kit.pipeline.orchestrate_write.orchestrate_write`

Source path: `src/fabricops_kit/pipeline/orchestrate_write.py`

Frozen source ref: `v0.2.5`

[View frozen source](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/v0.2.5/src/fabricops_kit/pipeline/orchestrate_write.py)

Signature: `orchestrate_write(dataframe: 'Any', *, sources: 'Iterable[dict[str, Any]]', store: 'str', schema: 'str | None', table_name: 'str', write_mode: 'str', write_parameters: 'dict[str, Any] | None' = None, contracts: 'dict[str, Any] | None' = None, repartition_by: 'int | None' = None, frequency_enabled: 'bool' = True, frequency_top_n: 'int | None' = 5, spark_session=None, verbose: 'bool' = True) -> 'dict[str, Any]'`

## Description

Execute the standard FabricOps governed Write lifecycle.

## Parameters

dataframe : object
    Transformed Spark DataFrame to validate and publish.
sources : iterable of dict
    Governed source results containing ``table_id``.
store : str
    Configured destination store key.
schema : str, optional
    Physical target schema.
table_name : str
    Physical target table name.
write_mode : str
    Notebook-facing Write mode forwarded to :func:`pipeline_write` as its governed load strategy.
write_parameters : dict, optional
    Parameters for the selected Write mode, forwarded to :func:`pipeline_write`
    as ``load_strategy_parameters``. For example, SCD1 requires
    ``key_columns``; SCD2 requires ``key_columns`` and ``effective_column``
    and may also define ``tracked_columns``.
contracts : dict, optional
    ``widget_select_data_contract`` result used to choose Validate or
    Enforce publication behaviour. Both modes run the same Guardrails.
repartition_by : int, optional
    Spark write partition count.
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
    Write identity and capability results. The top-level ``dataframe`` is
    the prepared input after Sensitive Data treatment, in both Validate
    and Enforce modes. It is the Write input, not necessarily the persisted
    target after Append, SCD1, or SCD2. ``sensitive_result`` retains its
    nested ``dataframe`` result. ``published`` is false when a Validate-mode
    contract passes without publication.

## Usage notes

Both contract modes run Schema, Sensitive Data, Source Drift, Data Quality,
and Guardrail Coverage identically. Validate then returns without writing;
Enforce continues through Write and persisted-target Profile. Existing
metadata and Source Observation commit behaviour remains owned by
``pipeline_write``. The returned ``dataframe`` is the prepared Write input,
not a reread of the persisted target; Append, SCD1, and SCD2 may produce a
different target state. No DataFrame is displayed or materialized for this
return value.

[Back to release overview](../index.md)

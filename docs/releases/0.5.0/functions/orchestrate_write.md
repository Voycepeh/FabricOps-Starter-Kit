<!-- Generated file. Edit docs/releases/manifests/0.5.0.yml or the authoritative source metadata and regenerate. -->

# `orchestrate_write`

<span class="fabricops-release-status fabricops-release-status--live">Live</span>

Package version: `0.5.0`

Qualified callable: `fabricops_kit.pipeline.orchestrate_write.orchestrate_write`

Source path: `src/fabricops_kit/pipeline/orchestrate_write.py`

Frozen source ref: `v0.5.0`

[View frozen source](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/v0.5.0/src/fabricops_kit/pipeline/orchestrate_write.py)

Signature: `orchestrate_write(dataframe: 'Any', *, store: 'str', schema: 'str | None' = None, table_name: 'str | None' = None, write_mode: 'str', write_parameters: 'dict[str, Any] | None' = None, repartition_by: 'int | None' = None, existing_mapping=None, verbose: 'bool' = False, dq_diagnostics: 'str' = 'sample', relative_path: 'str | None' = None, file_format: 'str | None' = None, write_options: 'dict[str, Any] | None' = None) -> 'dict[str, Any]'`

## Description

Evaluate or publish a target using the active pipeline's runtime.

## Parameters

dataframe : object
    Transformed Spark DataFrame; Sensitive Data treatment prepares the input.
store : str
    Configured target store key.
schema : str or None
    Explicit physical table schema; pass None for a schemaless store or omit for files.
table_name : str
    Physical target table name; omit for file destinations.
write_mode : str
    Table strategies: overwrite, append_all, append_new_only, scd1, scd2,
    captured exactly by Pipeline Activation. File modes: overwrite, append_all.
relative_path : str, optional
    Exact destination beneath the configured Lakehouse Files area.
file_format : {"csv", "parquet", "json"}, optional
    Required with relative_path. JSON is newline-delimited.
write_options : dict, optional
    Spark file writer options. Cannot override destination, mode or layout.
write_parameters : dict, optional
    Strategy parameters including SCD key_columns and SCD2 effective_column.
existing_mapping : object, optional
    Caller-managed Sensitive Data mapping; incompatible with a configured vault.
    Existing assignments are reused. The returned sensitive_result.support_mapping
    remains caller-owned; persist it only in persistent workflows, then unpersist() its
    cache after consumption. A configured restricted mapping store is read-only
    during Dry Run and reused/updated during persistent writes. Failures release the cache.
repartition_by : int, optional
    Physical write partition count for persistent modes. File exports apply
    this before staging: small output coalesces to one file; distributed
    overflow and append_all preserve the requested partition count.
verbose : bool
    Print concise stages and outcome when True; the execution widget reports automatically by default.
dq_diagnostics : {"sample", "none", "full"}
    Exact metrics with bounded samples, no samples or lazy full violations.

## Return value

dict
    Final prepared Write input under ``dataframe``, selected contract, execution identity, validation results,
    write metrics, publication state and profiling outcome. Per-source
    Source Drift results remain under ``source_drift_results``; the independent
    pipeline decision is under ``source_drift_decision``. Dry Run returns
    processing diagnostics without publication; persistent modes return the
    actual publication outcome. The DataFrame includes Sensitive Data treatment,
    row hash and target audit columns, plus SCD2 lifecycle columns where applicable.
    Append New Only returns only rows submitted for insertion. SCD previews
    represent processing input, not the reconstructed post-merge destination.
    Persistent modes return an eagerly materialized, caller-owned snapshot of
    the exact physical writer input. It remains inspectable after publication;
    call ``result["dataframe"].unpersist()`` when inspection is complete.
    File results instead return the supplied DataFrame without caching or
    table preparation, a source_id, resolved_path and filesystem write_metrics.
    File output_layout, overflow_occurred and overflow_reason describe the actual
    publication and are retained in file_write_parameters_json on the operation.
    Dry Run leaves actual layout and overflow unknown (None) and returns a
    publication_status=not_published because it does not stage or publish output.
    ``rows_committed`` measures this attempt; ``total_target_rows`` is the
    destination total where profiling provides it.

Raises RuntimeError when no pipeline is active or a persistent stage fails, and
ValueError for an invalid operation or inconsistent approved configuration.

## Usage notes

Not documented in the source docstring.

[Back to release overview](../index.md)

<!-- Generated file. Edit docs/releases/manifests/0.5.1.yml or the authoritative source metadata and regenerate. -->

# `orchestrate_read`

<span class="fabricops-release-status fabricops-release-status--live">Live</span>

Package version: `0.5.1`

Qualified callable: `fabricops_kit.pipeline.orchestrate_read.orchestrate_read`

Source path: `src/fabricops_kit/pipeline/orchestrate_read.py`

Frozen source ref: `v0.5.1`

[View frozen source](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/v0.5.1/src/fabricops_kit/pipeline/orchestrate_read.py)

Signature: `orchestrate_read(*, store: 'str', schema: 'str | None' = None, table_name: 'str | None' = None, read_mode: 'str' = 'full', query: 'str | None' = None, read_parameters: 'dict[str, Any] | None' = None, target_store: 'str | None' = None, target_schema: 'str | None' = None, target_table_name: 'str | None' = None, verbose: 'bool' = False, dq_diagnostics: 'str' = 'sample', relative_path: 'str | None' = None, file_format: 'str | None' = None, read_options: 'dict[str, Any] | None' = None) -> 'dict[str, Any]'`

## Description

Read a source using the active pipeline's contracts and runtime.

## Parameters

store : str
    Configured source store key.
schema : str or None
    Explicit physical schema; pass None for a schemaless store.
table_name : str
    Physical source table name.
read_mode : {"full", "incremental"}
    Full reads profile the source; incremental reads retain checkpoint bounds.
read_parameters : dict, optional
    Required for incremental reads; Engineering watermark_column captured by Pipeline Activation.
target_store : str, optional
    Configured target store key; required for incremental reads.
target_schema : str, optional
    Physical target schema; omit for a schemaless store or configured default.
target_table_name : str, optional
    Physical target table name; required for incremental reads. The resolved
    target must be an authorized target participant in the active plan.
    Source and target stores may route to different workspaces.
query : str, optional
    Read-only Spark SQL on a Lakehouse or T-SQL on a Warehouse, for full
    reads only. Lakehouse SQL binds the declared source through configured
    OneLake routing. Simple integer TOP projections can convert to LIMIT;
    complex T-SQL requires native Spark SQL and otherwise raises ValueError.
relative_path : str, optional
    File, folder or wildcard selector beneath the configured Lakehouse Files root.
    Brace expansion is unsupported because alternatives can escape that root.
    Mutually exclusive with table_name, schema, query and target coordinates.
file_format : {"csv", "json", "parquet", "excel"}, optional
    Required for file reads. Uses the corresponding foundational reader.
read_options : dict, optional
    Format-specific reader keyword settings, retained exactly for approval.
    Options cannot override the source location or execution context.
verbose : bool
    Print concise stage outcomes and summary.
dq_diagnostics : {"sample", "none", "full"}
    Rule metrics plus bounded examples, no examples, or lazy full failures.

## Return value

dict
    Governed source dataframe, execution identity, Guardrail outcomes, read_metrics, profile_result and orchestration_stages.
    ``read_metrics.rows_read`` and the notebook summary describe the exact
    returned scope. For incremental reads this is the target-specific batch,
    never the complete physical Source Observation count.

Raises RuntimeError when no pipeline is active or a persistent stage fails, and
ValueError for an invalid operation or inconsistent approved configuration.

## Usage notes

Not documented in the source docstring.

[Back to release overview](../index.md)

<!-- Generated file. Edit docs/releases/manifests/0.3.0.yml or the authoritative source metadata and regenerate. -->

# `orchestrate_read`

<span class="fabricops-release-status fabricops-release-status--live">Live</span>

Package version: `0.3.0`

Qualified callable: `fabricops_kit.pipeline.orchestrate_read.orchestrate_read`

Source path: `src/fabricops_kit/pipeline/orchestrate_read.py`

Frozen source ref: `v0.3.0`

[View frozen source](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/v0.3.0/src/fabricops_kit/pipeline/orchestrate_read.py)

Signature: `orchestrate_read(*, store: 'str', schema: 'str | None', table_name: 'str', read_mode: 'str' = 'full', query: 'str | None' = None, read_parameters: 'dict[str, Any] | None' = None, target_table_id: 'str | None' = None, verbose: 'bool' = False, dq_diagnostics: 'str' = 'sample') -> 'dict[str, Any]'`

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
    Incremental watermark_column; must agree with the selected contract.
target_table_id : str, optional
    Required target for incremental reads, also a participant in the plan.
query : str, optional
    Read-only Warehouse query, supported for full reads only.
verbose : bool
    Print concise stage outcomes and summary.
dq_diagnostics : {"sample", "none", "full"}
    Rule metrics plus bounded examples, no examples, or lazy full failures.

## Return value

dict
    Governed source dataframe, execution identity, Guardrail outcomes, read_metrics, profile_result and orchestration_stages.

Raises RuntimeError when no pipeline is active or a persistent stage fails, and
ValueError for an invalid operation or inconsistent approved configuration.

## Usage notes

Not documented in the source docstring.

[Back to release overview](../index.md)

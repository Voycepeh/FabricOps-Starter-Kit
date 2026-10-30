<!-- Generated file. Edit docs/releases/manifests/0.3.0.yml or the authoritative source metadata and regenerate. -->

# `orchestrate_write`

<span class="fabricops-release-status fabricops-release-status--live">Live</span>

Package version: `0.3.0`

Qualified callable: `fabricops_kit.pipeline.orchestrate_write.orchestrate_write`

Source path: `src/fabricops_kit/pipeline/orchestrate_write.py`

Frozen source ref: `v0.3.0`

[View frozen source](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/v0.3.0/src/fabricops_kit/pipeline/orchestrate_write.py)

Signature: `orchestrate_write(dataframe: 'Any', *, store: 'str', schema: 'str | None', table_name: 'str', write_mode: 'str', write_parameters: 'dict[str, Any] | None' = None, repartition_by: 'int | None' = None, existing_mapping=None, verbose: 'bool' = False, dq_diagnostics: 'str' = 'sample') -> 'dict[str, Any]'`

## Description

Evaluate or publish a target using the active pipeline's runtime.

## Parameters

dataframe : object
    Transformed Spark DataFrame; Sensitive Data treatment prepares the input.
store : str
    Configured target store key.
schema : str or None
    Explicit physical schema; pass None for a schemaless store.
table_name : str
    Physical target table name.
write_mode : {"overwrite", "append", "scd1", "scd2"}
    Proposed strategy; must match the selected contract processing definition.
write_parameters : dict, optional
    Strategy parameters including SCD key_columns and SCD2 effective_column.
existing_mapping : object, optional
    Caller-managed Sensitive Data mapping; incompatible with a configured vault.
    Existing assignments are reused. The returned sensitive_result.support_mapping
    remains caller-owned; persist it only in persistent workflows, then unpersist() its
    cache after consumption. A configured restricted mapping store is read-only
    during Dry Run and reused/updated during persistent writes. Failures release the cache.
repartition_by : int, optional
    Physical write partition count for persistent modes.
verbose : bool
    Print concise stages and outcome when True; the execution widget reports automatically by default.
dq_diagnostics : {"sample", "none", "full"}
    Exact metrics with bounded samples, no samples or lazy full violations.

## Return value

dict
    Prepared dataframe, selected contract, execution identity, validation results,
    write metrics, publication state and profiling outcome. Dry Run returns
    processing diagnostics without publication; persistent modes return the
    actual publication outcome.

Raises RuntimeError when no pipeline is active or a persistent stage fails, and
ValueError for an invalid operation or inconsistent approved configuration.

## Usage notes

Not documented in the source docstring.

[Back to release overview](../index.md)

<!-- Generated file. Edit docs/releases/manifests/0.5.1.yml or the authoritative source metadata and regenerate. -->

# `finalize_pipeline`

<span class="fabricops-release-status fabricops-release-status--live">Live</span>

Package version: `0.5.1`

Qualified callable: `fabricops_kit.pipeline.finalize_pipeline.finalize_pipeline`

Source path: `src/fabricops_kit/pipeline/finalize_pipeline.py`

Frozen source ref: `v0.5.1`

[View frozen source](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/v0.5.1/src/fabricops_kit/pipeline/finalize_pipeline.py)

Signature: `finalize_pipeline(pipeline=None, *, failed=False)`

## Description

Finalize execution or reopen persisted Engineering deployment/recovery controls.

## Parameters

pipeline : PipelineSession, optional
    Execution returned by setup_pipeline. Retain it for repeat finalization.
failed : bool, default=False
    Mark a caught project failure; recorded failures cannot become success.

## Return value

dict
    Final execution summary. For persistent modes this is the
    METADATA_PIPELINE_RUN snapshot; Dry Run returns the in-memory equivalent.
    When pipeline Source Drift is enabled, adds a source_drift diagnostic
    summary and separate baseline acceptance status without altering the
    immutable Run record. Failed or unconfirmed baseline acceptance does
    not roll back completed target publications. An unconfirmed outcome
    requires inspection of immutable acceptance history before retrying.
    Each operation retains legacy rows_read/rows_written plus its available
    detailed Read or strategy-specific Write metrics. Missing fields on
    historical records remain valid and display as not captured. Prepared Writes
    additionally retain operations[].lineage: a versioned graph of source columns,
    transformations and explicit coverage gaps. Persistent finalization also
    materializes scalar versioned dependency facts in METADATA_DATA_LINEAGE.
    lineage_projection reports the separate projection outcome; a projection
    failure after Run commit is retryable via finalize_pipeline(pipeline)
    without replaying business Writes. Dry Run retains graphs only in memory.
    When no session is active, returns the resolved pipeline_id and handoff
    (the displayed controls and their state/actions), without a Run record.

## Usage notes

Not documented in the source docstring.

[Back to release overview](../index.md)

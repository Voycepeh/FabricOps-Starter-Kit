<!-- Generated file. Edit docs/releases/manifests/0.3.0.yml or the authoritative source metadata and regenerate. -->

# `finalize_pipeline`

<span class="fabricops-release-status fabricops-release-status--live">Live</span>

Package version: `0.3.0`

Qualified callable: `fabricops_kit.pipeline.finalize_pipeline.finalize_pipeline`

Source path: `src/fabricops_kit/pipeline/finalize_pipeline.py`

Frozen source ref: `v0.3.0`

[View frozen source](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/v0.3.0/src/fabricops_kit/pipeline/finalize_pipeline.py)

Signature: `finalize_pipeline(pipeline=None, *, failed=False)`

## Description

Finalize a Dry Run, Ungoverned or Governed execution accurately.

## Parameters

pipeline : PipelineSession, optional
    Execution returned by setup_pipeline. Retain it for repeat finalization.
failed : bool, default=False
    Mark a caught project failure; recorded failures cannot become success.

## Return value

dict
    Final execution summary. For persistent modes this is the
    METADATA_PIPELINE_RUN snapshot; Dry Run returns the in-memory equivalent.

## Usage notes

Not documented in the source docstring.

[Back to release overview](../index.md)

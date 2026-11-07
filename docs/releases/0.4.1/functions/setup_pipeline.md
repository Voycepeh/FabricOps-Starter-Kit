<!-- Generated file. Edit docs/releases/manifests/0.4.1.yml or the authoritative source metadata and regenerate. -->

# `setup_pipeline`

<span class="fabricops-release-status fabricops-release-status--live">Live</span>

Package version: `0.4.1`

Qualified callable: `fabricops_kit.pipeline.setup_pipeline.setup_pipeline`

Source path: `src/fabricops_kit/pipeline/setup_pipeline.py`

Frozen source ref: `v0.4.1`

[View frozen source](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/v0.4.1/src/fabricops_kit/pipeline/setup_pipeline.py)

Signature: `setup_pipeline(*, pipeline_mode: 'str' = 'Ungoverned', observe_source: 'bool' = False, source_observation_days: 'int | None' = None)`

## Description

Start a pipeline using the current Fabric notebook identity and one execution mode.

## Parameters

pipeline_mode : {"Dry Run", "Ungoverned", "Governed"}, default="Ungoverned"
    Preview, publish without governance, or enforce activated governance.

observe_source : bool, default=False
    Manually request a full physical Source Observation for this execution.
source_observation_days : int or None, default=None
    Automatically observe after this many days since the last accepted full
    observation. None disables automatic observation. Manual requests override
    the interval. Incremental SQL scope does not restrict observation. Baselines
    are accepted only with verified target publication; failed or no-op writes
    do not consume the interval. Changed fingerprints are diagnostic unless
    a separately configured Source Drift policy blocks publication.

## Return value

PipelineSession
    Context-local Read/Write execution and in-memory report. Call
    finalize_pipeline after every Read, transformation and Write completes.

## Usage notes

Call setup_notebook first. Spark and Fabric identity come from that setup.
The current Fabric Notebook ID establishes the logical Pipeline ID. The
Pipeline Registry maps promoted physical notebook IDs back to the original
identity; no identity is declared in notebook source. Repeated setup closes
the previous execution. Dry Run never writes Registry, Run,
profiling results or Processing State. Completed captured Dry Runs retain
serializable saved-definition/test claims in Engineering Files for submission.
Finalize displays the package download and explicit deployment/recovery controls.
Governed setup validates the active deployed notebook and approved executable
code/configuration; outputs, counts and Markdown may change. Setup never
deploys, freezes an edited source, or repairs a notebook automatically.
Persistent runs record final outcomes;
a successful Write does not imply successful whole-notebook completion.

[Back to release overview](../index.md)

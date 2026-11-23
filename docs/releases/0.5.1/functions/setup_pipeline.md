<!-- Generated file. Edit docs/releases/manifests/0.5.1.yml or the authoritative source metadata and regenerate. -->

# `setup_pipeline`

<span class="fabricops-release-status fabricops-release-status--live">Live</span>

Package version: `0.5.1`

Qualified callable: `fabricops_kit.pipeline.setup_pipeline.setup_pipeline`

Source path: `src/fabricops_kit/pipeline/setup_pipeline.py`

Frozen source ref: `v0.5.1`

[View frozen source](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/v0.5.1/src/fabricops_kit/pipeline/setup_pipeline.py)

Signature: `setup_pipeline(*, pipeline_mode: 'str' = 'Ungoverned', profiling_enabled: 'bool' = True, profiling_interval_days: 'int' = 1, profiling_max_rows: 'int | None' = None, grain_discovery_enabled: 'bool' = False, frequency_enabled: 'bool' = False, source_drift_enabled: 'bool' = False, source_drift_interval_days: 'int' = 1, source_drift_block: 'bool' = True)`

## Description

Start a pipeline using the current Fabric notebook identity and one execution mode.

## Parameters

pipeline_mode : {"Dry Run", "Ungoverned", "Governed"}, default="Ungoverned"
    Preview, publish without governance, or enforce activated governance.

profiling_enabled : bool, default=True
    Enable Standard profiling independently of Grain discovery and Frequency.
profiling_interval_days : int, default=1
    Positive integer interval since the latest confirmed physical-table
    Standard completion with sufficient scope, shared across pipelines.
    Full-table requests ignore bounded completions; bounded requests may reuse
    full completions or completions with an equal or larger requested bound.
profiling_max_rows : int or None, default=None
    None profiles the complete physical table (the prepared DataFrame for
    Dry Run Writes). A positive integer bounds each
    enabled activity using an arbitrary row selection; statistics describe only
    that selection. This does not guarantee a physical read of only that many
    rows. Saved results carry their scope. Guardrails and Source Observation
    always use their own required input, independently of this limit.
grain_discovery_enabled : bool, default=False
    Discover candidate Grain keys once per physical table and sufficient scope.
    Does not control mandatory Grain Guardrails.
frequency_enabled : bool, default=False
    Profile value frequencies once per physical table and sufficient scope.

source_drift_enabled : bool, default=False
    Observe complete physical sources automatically during Read, independently
    of profiling limits and incremental checkpoints. Read every source before
    any Write; the first Write closes the participating Read set.
source_drift_interval_days : int, default=1
    Positive interval since the latest confirmed successful acceptance for the
    physical source, shared across pipelines. Failed or incomplete runs and
    nonpublishing Writes do not advance observation history.
source_drift_block : bool, default=True
    Block publication on confirmed removals, modifications, schema changes
    or unavailable observations. Additions alone are reported and never block
    publication, including normal incremental source growth. False permits
    warnings; new baselines still require successful finalization and verified
    required publications.
    The first exact snapshot does not invent historical changes.

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

<!-- Generated file. Edit docs/releases/manifests/0.3.1.yml or the authoritative source metadata and regenerate. -->

# `setup_pipeline`

<span class="fabricops-release-status fabricops-release-status--live">Live</span>

Package version: `0.3.1`

Qualified callable: `fabricops_kit.pipeline.setup_pipeline.setup_pipeline`

Source path: `src/fabricops_kit/pipeline/setup_pipeline.py`

Frozen source ref: `v0.3.1`

[View frozen source](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/v0.3.1/src/fabricops_kit/pipeline/setup_pipeline.py)

Signature: `setup_pipeline(*, pipeline_id: 'str | None' = None, pipeline_mode: 'str' = 'Ungoverned', new_pipeline: 'bool' = False, previous_workspace_id: 'str | None' = None, previous_notebook_id: 'str | None' = None)`

## Description

Start an isolated pipeline in Dry Run, Ungoverned or Governed mode.

## Parameters

pipeline_id : str | None, optional
    Permanent UUIDv4. Omit to recover the exact notebook binding or register
    a new UUID in Ungoverned mode. Dry Run may use a session-only UUID and
    never registers it. Governed never allocates a new UUID.
    A changed same-workspace_id binding requires both previous notebook IDs.
pipeline_mode : {"Dry Run", "Ungoverned", "Governed"}, default="Ungoverned"
    Preview without writing, execute without contracts, or execute with
    activated contracts enforced.
new_pipeline : bool, default=False
    Explicitly create a new identity for an independent notebook copy. Omit
    pipeline_id when set. An already registered notebook is rejected.
previous_workspace_id, previous_notebook_id : str | None, optional
    Supply both old binding IDs to explicitly rebind a reuploaded notebook.
    Rebinding requires Ungoverned mode and no active Governed runs.

## Return value

PipelineSession
    Contract selection, pipeline_id containing the permanent UUID, registration
    details and the automatically refreshed execution report. Read and
    Write calls use this execution through a context-local binding.

## Usage notes

Call setup_notebook() first to initialize configuration and display notebook
readiness. This function reuses that configuration without rerunning
00_env_config or displaying the workspace_id summary. Cross-workspace
configuration is selected only through setup_notebook(config_workspace_id=...).
Repeated pipeline setup closes the preceding execution owned by this task.
Repeated notebook setup closes its pipeline and invalidates prior configuration,
including when the new setup fails. Changed runtime identity requires fresh
notebook setup.

Fabric cell events identify failures, not successful notebook completion.
Call finalize_pipeline after all Reads, transformations and Writes.
Neither a successful Write nor interpreter shutdown proves completion. Dry
Run finalization returns only a session summary and does not persist it.

[Back to release overview](../index.md)

# `setup_pipeline`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview reference-lifecycle-chip-prominent">Preview</span>
</p>

> This function is available for evaluation but is not part of the supported Live release contract. It may change without backward-compatibility guarantees.

Prepare Testing or resolve an approved workspace configuration for Live.


## Usage notes

Call after setup_notebook() and before Read, Transform and Write. Test registers or recovers the Pipeline ID automatically.


## Example usage

<div class="reference-example-usage" markdown="1">

```python
context = setup_notebook()
pipeline = setup_pipeline(pipeline_id="8f32a471-6c91-4b7e-9d13-2f0c947eab52", pipeline_mode="Ungoverned")
orders = orchestrate_read(store="Bronze", schema="demo", table_name="orders")
independent_copy = setup_pipeline(pipeline_mode="Ungoverned", new_pipeline=True)
reuploaded = setup_pipeline(pipeline_id=PIPELINE_ID, pipeline_mode="Ungoverned",
    previous_workspace_id=old_workspace_id, previous_notebook_id=old_notebook_id)
```

</div>

<details class="reference-signature-details" markdown="1">
<summary>Signature</summary>

## Signature

<div class="reference-api-definition" markdown="1">

```python
def setup_pipeline(
    *,
    pipeline_id: str | None=None,
    pipeline_mode: str='Ungoverned',
    new_pipeline: bool=False,
    previous_workspace_id: str | None=None,
    previous_notebook_id: str | None=None,
):
```

</div>

</details>

## Parameters

Required describes the Python signature. An optional parameter may still be needed for the selected mode or identity form; see its description. `—` means no signature default.

<div class="reference-input-table" markdown="1">

| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `pipeline_id` | `str \| None` | No | `None` | Permanent UUIDv4. Omit to recover the exact notebook binding or register a new UUID in Ungoverned mode. Dry Run may use a session-only UUID and never registers it. Governed never allocates a new UUID. A changed same-workspace_id binding requires both previous notebook IDs. |
| `pipeline_mode` | `str` | No | `'Ungoverned'` | Preview without writing, execute without contracts, or execute with activated contracts enforced. |
| `new_pipeline` | `bool` | No | `False` | Explicitly create a new identity for an independent notebook copy. Omit pipeline_id when set. An already registered notebook is rejected. |
| `previous_workspace_id` | `str \| None` | No | `None` | Supply both old binding IDs to explicitly rebind a reuploaded notebook. Rebinding requires Ungoverned mode and no active Governed runs. |
| `previous_notebook_id` | `str \| None` | No | `None` | Not documented yet |

</div>

## Returns

PipelineSession
    Contract selection, pipeline_id containing the permanent UUID, registration
    details and the automatically refreshed execution report. Read and
    Write calls use this execution through a context-local binding.

### Return interpretation

Returns a context-local execution session exposing pipeline_id, contract selection and automatic reporting; finalize_pipeline records completion and commits Test results; interrupted runs remain incomplete.

## Raises / Errors

ValueError
    For an invalid UUIDv4, conflicting notebook binding, unsupported mode or
    missing Governed activation.
RuntimeError
    If setup_notebook() has not completed successfully for the current
    execution, or a Spark session is unavailable.

### Common failure causes

- Missing, failed or outdated setup_notebook() initialization.
- Invalid frozen contract selections.
- Missing notebook registration or approved Live configuration.

## Notes

<div class="reference-docstring-notes" markdown="1">

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

</div>

## Behavior and scope

<div class="reference-docstring-intro" markdown="1">

Dry Run evaluates real reads, transformations, profiling and optionally
selected contract Guardrails without persisting target data or operational
state. Ungoverned executes without Data Contracts while retaining operational
checks and blocks writes to tables already governed in the workspace.
Governed resolves only activated workspace authority and enforces its exact
contract versions, destinations and ownership throughout the run.
Spark and supported Fabric runtime identity are resolved internally. The caller workspace and notebook IDs are required for registration.

</div>

## See also

No related guides documented.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/pipeline/setup_pipeline.py:130`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline/setup_pipeline.py#L130-L222">View on GitHub</a>
</div>


<details class="reference-implementation-details" markdown="1">
<summary>Maintainer architecture details</summary>

## Contract impact

| Property | Value |
| --- | --- |
| Lifecycle | <span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview">Preview</span> |
| Live since | — |
| Discontinued in | — |
| Contract classification | Preview public function |
| Contract risk | Preview |
| Live-critical dependencies | 0 |


</details>

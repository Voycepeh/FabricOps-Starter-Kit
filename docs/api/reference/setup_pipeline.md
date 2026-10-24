# `setup_pipeline`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview reference-lifecycle-chip-prominent">Preview</span>
</p>

> This function is available for evaluation but is not part of the supported Live release contract. It may change without backward-compatibility guarantees.

Prepare Testing or resolve an approved environment configuration for Live.


## Usage notes

Use once before Read, Transform and Write with pipeline_id and pipeline_mode.


## Example usage

<div class="reference-example-usage" markdown="1">

```python
contracts = setup_pipeline(pipeline_id="8f32a471-6c91-4b7e-9d13-2f0c947eab52", pipeline_mode="Test")
orders = orchestrate_read(store="Bronze", schema="demo", table_name="orders")
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
    pipeline_mode: str='Test',
    config_workspace_id: str | None=None,
):
```

</div>

</details>

## Parameters

Required describes the Python signature. An optional parameter may still be needed for the selected mode or identity form; see its description. `—` means no signature default.

<div class="reference-input-table" markdown="1">

| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `pipeline_id` | `str \| None` | No | `None` | Permanent UUIDv4. Omit to recover the exact notebook binding or register a new UUID. Save the displayed UUID in the notebook for promotion. Changed same-environment bindings require explicit rebind_pipeline. |
| `pipeline_mode` | `str` | No | `'Test'` | Evaluation-only operations or execution under an approved manifest. |
| `config_workspace_id` | `str \| None` | No | `None` | Workspace hosting 00_env_config. Defaults to the current workspace. Supply an ID only when using a shared cross-workspace configuration. |

</div>

## Returns

PipelineSession
    Contract selection, pipeline_id containing the permanent UUID, registration
    details and the automatically refreshed execution report. Read and
    Write calls use this execution through a context-local binding.

### Return interpretation

Returns a context-local execution session with contract selection and automatic reporting; finalize_pipeline records completion and returns Test results; interrupted runs remain incomplete.

## Raises / Errors

ValueError
    For an invalid UUIDv4, conflicting notebook binding, unsupported mode or
    missing Live approval.
RuntimeError
    For missing environment configuration or an unavailable Spark session.

### Common failure causes

- Missing explicit table choices or invalid frozen contract selections.
- Unsafe Testing write destination.
- Missing complete governed Testing for activation or approved Live configuration.

## Notes

<div class="reference-docstring-notes" markdown="1">

Workspace configuration is loaded through the same initialization as
setup_notebook. Load the current workspace configuration by default, or
supply config_workspace_id for a shared deployment. The caller workspace
determines the environment in both cases. Initialization prints the FabricOps
version, resolved configuration and targets, and startup readiness in the
calling notebook.

Fabric cell events identify failures, not successful notebook completion.
Call finalize_pipeline after all Reads, transformations and Writes.
Neither a successful Write nor interpreter shutdown proves completion. Test
results remain in memory after finalization.

</div>

## Behavior and scope

<div class="reference-docstring-intro" markdown="1">

Test evaluates reads, transformations and Guardrails without business or
metadata commits, including finalization. Only administrative Engineering
registration may write in Test. finalize_pipeline returns in-memory results
for explicit activation review. Select frozen contracts in the returned interface before
the first operation; headless Test explicitly uses No Contract. Live resolves
only the approved environment manifest and retains revision/ownership checks.
Spark and supported Fabric runtime identity are resolved internally. The caller workspace and notebook IDs are required for registration.

</div>

## See also

No related guides documented.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/pipeline/setup_pipeline.py:130`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline/setup_pipeline.py#L130-L201">View on GitHub</a>
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

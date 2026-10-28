# `finalize_pipeline`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview reference-lifecycle-chip-prominent">Preview</span>
</p>

> This function is available for evaluation but is not part of the supported Live release contract. It may change without backward-compatibility guarantees.

Complete execution and return Test results or commit the Live outcome.


## Usage notes

Call after all Reads, transformations and Writes, including read-only runs.


## Example usage

<div class="reference-example-usage" markdown="1">

```python
pipeline = setup_pipeline(pipeline_id="8f32a471-6c91-4b7e-9d13-2f0c947eab52", pipeline_mode="Test")
source = orchestrate_read(store="Bronze", schema="demo", table_name="orders")
pipeline_result = finalize_pipeline(pipeline)
```

</div>

<details class="reference-signature-details" markdown="1">
<summary>Signature</summary>

## Signature

<div class="reference-api-definition" markdown="1">

```python
def finalize_pipeline(pipeline=None, *, failed=False)
```

</div>

</details>

## Parameters

Required describes the Python signature. An optional parameter may still be needed for the selected mode or identity form; see its description. `—` means no signature default.

<div class="reference-input-table" markdown="1">

| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `pipeline` | `PipelineSession` | No | `None` | Execution returned by setup_pipeline. Retain it for repeat finalization. |
| `failed` | `bool` | No | `False` | Mark a caught project failure; recorded failures cannot become success. |

</div>

## Returns

dict
    Final METADATA_PIPELINE_RUN snapshot. Repeating with the same session
    returns the original result without additional successful commits.

## Raises / Errors

ValueError
    If pipeline is not a setup_pipeline session or audit identity is missing.
RuntimeError
    If notebook setup is invalid, runtime identity has changed, another task
    owns the execution, or metadata publication fails. Run and Guardrail IDs
    remain stable for supported publication retries. A Test profile-publication
    failure records a failed outcome and requires a new Test execution.

## Behavior and scope

<div class="reference-docstring-intro" markdown="1">

Call once after all Reads, transformations and Writes, including read-only
runs. Pass the session returned by setup_pipeline, or omit it to use the
current execution. Set failed=True when a project exception was caught.
A successful Write or cell never completes the whole pipeline by itself.
Open sessions require the current initialized notebook configuration and
runtime identity, whether passed explicitly or selected implicitly. Already
closed sessions retain their recorded outcome for repeat finalization.

Test Read/Write operations do not commit business or operational metadata.
Explicit finalization commits the complete Test run and Guardrail results
for Governance review. Successful Test finalization also saves the already
calculated observations to METADATA_DATA_CATALOGUE, METADATA_DATA_PROFILED
and METADATA_DATA_PROFILED_FREQUENCY for Data Contract authoring, without
repeating the profiling scans or publishing business data.
Failed and incomplete runs do not publish profiling observations. The activation
widget reads the committed run and Guardrail records. Complete governed Testing can then be approved. Failed, partial and No Contract
runs cannot authorize activation. Live finalization releases its reservation
after recording the final outcome. Interrupted runs remain incomplete.

</div>

## See also

No related guides documented.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/pipeline/finalize_pipeline.py:10`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline/finalize_pipeline.py#L10-L79">View on GitHub</a>
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

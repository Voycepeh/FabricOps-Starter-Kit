# `finalize_pipeline`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview reference-lifecycle-chip-prominent">Preview</span>
</p>

> This function is available for evaluation but is not part of the supported Live release contract. It may change without backward-compatibility guarantees.

Seal and persist complete logical pipeline run evidence.


## Usage notes

Call after every declared operation, including Read-only pipelines.


## Example usage

<div class="reference-example-usage" markdown="1">

```python
run = finalize_pipeline(plan)
run["status"]
```

```text
'succeeded'
```

</div>

<details class="reference-signature-details" markdown="1">
<summary>Signature</summary>

## Signature

<div class="reference-api-definition" markdown="1">

```python
def finalize_pipeline(execution_plan, *, failed=False, spark_session=None)
```

</div>

</details>

## Parameters

Required describes the Python signature. An optional parameter may still be needed for the selected mode or identity form; see its description. `—` means no signature default.

<div class="reference-input-table" markdown="1">

| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `execution_plan` | `PipelineExecutionPlan` | Yes | `—` | Shared plan returned by setup_pipeline. Use after all Reads, transforms and Writes, including Read-only runs. No Write or Guardrail row finalizes a run. |
| `failed` | `bool` | No | `False` | Set True when project transformation or notebook logic failed. Orchestration failures are recorded automatically. Unfinalized runs remain incomplete. |
| `spark_session` | `object` | No | `None` | Spark session for configured Engineering metadata persistence. |

</div>

## Returns

dict
    Persisted METADATA_PIPELINE_RUN snapshot. Only a complete Testing run with
    an available candidate fingerprint and no blocking or persistence failure
    qualifies_for_activation. Bootstrap never qualifies. This does not activate
    anything; current Live still uses existing Data Contract authority.
    Repeated finalization returns the same snapshot without another write.

## Raises / Errors

RuntimeError
    If evidence cannot be persisted; create a new plan for a retry. Metadata
    and business stores are separate transactions without cross-store atomicity.
ValueError
    If execution_plan is invalid.

## See also

No related guides documented.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/pipeline/finalize_pipeline.py:6`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline/finalize_pipeline.py#L6-L44">View on GitHub</a>
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

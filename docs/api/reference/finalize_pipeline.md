# `finalize_pipeline`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview reference-lifecycle-chip-prominent">Preview</span>
</p>

> This function is available for evaluation but is not part of the supported Live release contract. It may change without backward-compatibility guarantees.

Consolidate Data Contract results and finalize execution tracking.


## Usage notes

Call after all Reads, transformations and Writes, including read-only runs.


## Example usage

<div class="reference-example-usage" markdown="1">

```python
pipeline_result = finalize_pipeline(pipeline)
pipeline_result["status"]
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
| `execution_plan` | `—` | Yes | `—` | Not documented yet |
| `failed` | `—` | No | `False` | Not documented yet |
| `spark_session` | `—` | No | `None` | Not documented yet |

</div>

## Returns

Not documented yet

## Raises / Errors

Not documented yet

## Behavior and scope

<div class="reference-docstring-intro" markdown="1">

Call after every declared Read, transformation and Write, including read-only
runs. Reuses setup context and recorded results without counting DataFrames.
Set failed=True for a caught project exception; orchestrator failures are
recorded automatically. A stopped notebook remains incomplete.

Returns the persisted METADATA_PIPELINE_RUN summary with exact Data Contract
versions, status and activation revision. Repeated finalization returns the
original snapshot without another write. Existing execution reservations are
released after persistence. Metadata failure raises RuntimeError; invalid
execution_plan raises ValueError. Business writes and metadata remain separate
transactions. This function neither activates contracts nor verifies code.

</div>

## See also

No related guides documented.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/pipeline/finalize_pipeline.py:5`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline/finalize_pipeline.py#L5-L33">View on GitHub</a>
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

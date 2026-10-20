# `create_pipeline_execution_plan`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview reference-lifecycle-chip-prominent">Preview</span>
</p>

> This function is available for evaluation but is not part of the supported Live release contract. It may change without backward-compatibility guarantees.

Create explicit immutable Testing/Live execution authority for a pipeline.


## Usage notes

Use for scheduled execution or to freeze widget selections before Read.


## Example usage

<div class="reference-example-usage" markdown="1">

```python
plan = create_pipeline_execution_plan(
    execution_mode="testing", sources=PIPELINE_SOURCES, targets=PIPELINE_TARGETS,
    selections={source_id: {"no_contract": True}, target_id: {"no_contract": True}},
)
source = orchestrate_read(execution_plan=plan, store="Bronze", schema="demo", table_name="orders")
```

</div>

<details class="reference-signature-details" markdown="1">
<summary>Signature</summary>

## Signature

<div class="reference-api-definition" markdown="1">

```python
def create_pipeline_execution_plan(
    *,
    execution_mode,
    sources,
    targets,
    selections,
    context=None,
    spark_session=None,
):
```

</div>

</details>

## Parameters

Required describes the Python signature. An optional parameter may still be needed for the selected mode or identity form; see its description. `—` means no signature default.

<div class="reference-input-table" markdown="1">

| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `execution_mode` | `{"testing", "live"}` | Yes | `—` | Required for interactive and scheduled execution, independent of environment. |
| `sources` | `list of dict` | Yes | `—` | Actual source participants with store/schema/table_name or a registered canonical table_id. No historical Lineage is needed. |
| `targets` | `list of dict` | Yes | `—` | Actual target participants with store/schema/table_name or a registered table_id. |
| `selections` | `dict` | Yes | `—` | Exactly one choice per participating table_id: either ``{"no_contract": True}`` or exact ``contract_id`` and ``contract_version``. Live requires the active frozen version when one exists and never accepts an inactive candidate. No Contract cannot bypass an active version. |
| `context` | `dict` | No | `None` | Configured Fabric routing and runtime notebook identity. |
| `spark_session` | `object` | No | `None` | Spark session for metadata reads. |

</div>

## Returns

PipelineExecutionPlan
    Immutable mode, identities, and canonical frozen payload snapshots, with
    an isolated in-memory Guardrail journal shared by all Read/Write calls.
    Create a new plan after changing selections; pass the same plan explicitly
    to every orchestrator in the run. This function performs metadata reads only.

## Raises / Errors

ValueError
    If mode, identities or explicit selections are invalid, or Live would
    bypass an active contract. Corrupt payloads are errors, never No Contract.
RuntimeError
    If metadata contains ambiguous active versions or duplicate version rows.

## See also

No related guides documented.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/pipeline/create_pipeline_execution_plan.py:20`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline/create_pipeline_execution_plan.py#L20-L128">View on GitHub</a>
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

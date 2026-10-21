# `setup_pipeline`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview reference-lifecycle-chip-prominent">Preview</span>
</p>

> This function is available for evaluation but is not part of the supported Live release contract. It may change without backward-compatibility guarantees.

Prepare Testing or resolve an approved environment configuration for Live.


## Usage notes

Use before reads, transformations and writes; execute them inside with plan:.


## Example usage

<div class="reference-example-usage" markdown="1">

```python
plan = setup_pipeline(sources=SOURCES, targets=TARGETS, pipeline_id="hr-employees",
    interactive=False, selections=SELECTIONS, dependencies={}, configuration={})
with plan:
    source = orchestrate_read(execution_plan=plan, **READ_CONFIG)
    transformed = transform(source["dataframe"])
    result = orchestrate_write(transformed, execution_plan=plan, sources=[source], **WRITE_CONFIG)
```

</div>

<details class="reference-signature-details" markdown="1">
<summary>Signature</summary>

## Signature

<div class="reference-api-definition" markdown="1">

```python
def setup_pipeline(
    *,
    sources,
    targets,
    execution_mode='testing',
    selections=None,
    interactive=None,
    spark_session=None,
    context=None,
    pipeline_id=None,
    executable_sha256=None,
    dependencies=None,
    configuration=None,
    testing_writes=False,
):
```

</div>

</details>

## Parameters

Required describes the Python signature. An optional parameter may still be needed for the selected mode or identity form; see its description. `—` means no signature default.

<div class="reference-input-table" markdown="1">

| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `sources` | `—` | Yes | `—` | Not documented yet |
| `targets` | `—` | Yes | `—` | Not documented yet |
| `execution_mode` | `—` | No | `'testing'` | Not documented yet |
| `selections` | `—` | No | `None` | Not documented yet |
| `interactive` | `—` | No | `None` | Not documented yet |
| `spark_session` | `—` | No | `None` | Not documented yet |
| `context` | `—` | No | `None` | Not documented yet |
| `pipeline_id` | `—` | No | `None` | Not documented yet |
| `executable_sha256` | `—` | No | `None` | Not documented yet |
| `dependencies` | `—` | No | `None` | Not documented yet |
| `configuration` | `—` | No | `None` | Not documented yet |
| `testing_writes` | `—` | No | `False` | Not documented yet |

</div>

## Returns

Not documented yet

### Return interpretation

Interactive Testing returns a selector with build_plan(); headless execution returns an immutable plan. with plan: records the whole-run outcome automatically.

## Raises / Errors

Not documented yet

### Common failure causes

- Partial contract selections.
- Unsafe Testing write destination.
- Missing complete Testing or approved Live configuration.

## Behavior and scope

<div class="reference-docstring-intro" markdown="1">

Testing is interactive by default. Set interactive=False for automation and
provide exact contract_id/contract_version choices keyed by global table_id,
or omit selections for contract-free exploration. Select every participant's
frozen contract or No Contract for all; partial governance is rejected.
Stable pipeline_id is required and independent of notebook name or path.

testing_writes=True explicitly permits real Testing writes to the declared
target destinations, provided no Live pipeline owns them. Such writes have
real side effects, including target metadata, mappings and checkpoints.
False evaluates without publication. Guardrail diagnostics and run records
always persist to the central configured Metadata store.

Live is headless and resolves the environment's approved configuration
automatically. It rejects manual contract choices and pins one activation
revision. Notebook code, dependencies, transformation configuration, table
identity, destinations and ownership must match approval. Operational
differences allowed by the orchestrators warn and persist in the run record.

Returns an immutable PipelineExecutionPlan, or Testing widget state with
select_contract, build_plan and refresh. Execute the complete pipeline inside
``with plan:``; exit automatically persists success, failure or incompleteness.
This explicit boundary includes transformations and read-only pipelines.
Without the boundary, operation results remain incomplete and ineligible.
Missing executable/dependency identity also prevents qualifying success.

Raises ValueError for unsafe configuration or partial contract selection,
RuntimeError for metadata failures, stale authority or a reused run boundary.
Approval neither deploys notebooks nor writes business data.

</div>

## See also

No related guides documented.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/pipeline/setup_pipeline.py:130`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline/setup_pipeline.py#L130-L379">View on GitHub</a>
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

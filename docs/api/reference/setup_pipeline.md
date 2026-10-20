# `setup_pipeline`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview reference-lifecycle-chip-prominent">Preview</span>
</p>

> This function is available for evaluation but is not part of the supported Live release contract. It may change without backward-compatibility guarantees.

Bootstrap initial outputs or explicitly set up contract Testing/Live for each participant.


## Usage notes

Use before Read, including first-time bootstrap without historical Lineage.


## Example usage

<div class="reference-example-usage" markdown="1">

```python
plan = setup_pipeline(sources=PIPELINE_SOURCES, targets=PIPELINE_TARGETS)
selection = setup_pipeline(sources=PIPELINE_SOURCES, targets=PIPELINE_TARGETS, interactive=True)
testing_plan = selection["build_plan"]()
scheduled_plan = setup_pipeline(
    sources=PIPELINE_SOURCES, targets=PIPELINE_TARGETS, interactive=False,
    execution_mode="testing", selections=EXACT_SELECTIONS,
)
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
    execution_mode=None,
    selections=None,
    interactive=False,
    spark_session=None,
    context=None,
):
```

</div>

</details>

## Parameters

Required describes the Python signature. An optional parameter may still be needed for the selected mode or identity form; see its description. `—` means no signature default.

<div class="reference-input-table" markdown="1">

| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `sources` | `list of dict` | Yes | `—` | Explicit source participants: store/schema/table_name or registered table_id. Historical Lineage is optional and cannot introduce additional participants. |
| `targets` | `list of dict` | Yes | `—` | Explicit target participants with the same coordinate or table_id shape. |
| `execution_mode` | `{"bootstrap", "testing", "live"}` | No | `None` | Defaults to Bootstrap without interaction. Bootstrap creates and profiles initial outputs only while no participating frozen or active contract exists. Interactive setup defaults to Testing. Governed headless modes are explicit. |
| `selections` | `dict` | No | `None` | Exact per-table contract_id/contract_version; Testing also permits explicit no_contract=True when no active contract is bypassed. Live requires a contract for every participant. Required for headless Testing/Live; omitted for Bootstrap. Both paths use the same immutable plan builder. |
| `interactive` | `bool` | No | `False` | Defaults to False. If True, explicitly enable interactive contract Testing. If False, return the immutable plan directly without loading notebook UI packages or enumerating unrelated contract versions. |
| `spark_session` | `object` | No | `None` | Spark session for metadata reads. |
| `context` | `dict` | No | `None` | Configured environment routing and notebook identity. |

</div>

## Returns

dict or PipelineExecutionPlan
    Headless execution returns the immutable plan. Interactive execution returns
    state with execution_mode (initially testing), tables, controls,
    select_contract, set_mode, build_plan and refresh. Each table starts unselected.
    After executing the built plan, refresh shows its exact-version results
    in expandable sections alongside saved definitions and disabled states.
    Bootstrap needs no selections or build action and returns its plan directly.
    For interactive Testing, build_plan validates every choice and freezes
    the plan to pass to all Read and Write calls.
    Mode and selection edits are rejected after build_plan; create a new widget
    for the next run. Repeated build_plan calls return the same plan and journal.
    The widget never changes notebook globals, edits or activates contracts.

### Return interpretation

Default Bootstrap returns a plan with no UI or choices while no participant has frozen or active contracts. Explicit interactive Testing selects contracts and calls build_plan(); pass the same immutable plan to every Read and Write. For scheduled runs, set interactive=False with execution_mode and selections; the same builder returns the plan directly.

## Raises / Errors

ValueError
    For frozen/active contracts blocking Bootstrap, missing notebook identity,
    invalid payloads, unavailable selections or
    Live choices bypassing an active contract.
RuntimeError
    For ambiguous active versions, metadata-read failure, or edits to a built plan.

### Common failure causes

- Bootstrap would bypass a frozen or active contract.
- Missing notebook identity or explicit participant configuration.
- Ambiguous active versions.
- Invalid or mismatched frozen JSON.
- Live attempts to bypass an active frozen contract.

## See also

No related guides documented.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/pipeline/setup_pipeline.py:130`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline/setup_pipeline.py#L130-L400">View on GitHub</a>
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

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

Finalize every plan with finalize_pipeline(), including Read-only pipelines.
Live resolves only the saved exact Activated Pipeline version. Supply an
explicit deployment_path, and activated_pipeline_id once to save selection.
Subsequent unattended Live calls omit that ID; a changed version never replaces
the saved selection silently. replace_selection=True is an explicit switch.

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
    pipeline_id=None,
    executable_sha256=None,
    dependencies=None,
    configuration=None,
    deployment_path=None,
    activated_pipeline_id=None,
    replace_selection=False,
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
| `execution_mode` | `{"bootstrap", "testing", "live"}` | No | `None` | Defaults to Bootstrap without interaction. Bootstrap creates and profiles initial outputs only while no participating frozen contract exists. Interactive setup defaults to Testing. Governed headless modes are explicit. |
| `selections` | `dict` | No | `None` | Exact per-table contract_id/contract_version; Testing also permits explicit no_contract=True. Required for headless Testing and forbidden for Live. Live contracts resolve exclusively from an approved deployment manifest. |
| `interactive` | `bool` | No | `False` | Defaults to False. If True, explicitly enable interactive contract Testing. If False, return the immutable plan directly without loading notebook UI packages or enumerating unrelated contract versions. |
| `spark_session` | `object` | No | `None` | Spark session for metadata reads. |
| `context` | `dict` | No | `None` | Configured environment routing and notebook identity. |
| `pipeline_id` | `str` | No | `None` | Stable project-owned logical identity, portable across environments. Required for qualifying Testing evidence; never use a run or workspace identifier. |
| `executable_sha256` | `str` | No | `None` | Optional expected fingerprint of the deployed notebook's executable cells. Fabric observes the actual definition; a mismatched pin is rejected. Outputs, display metadata and physical bindings are excluded. Unavailable identity leaves Testing incomplete. Keep helpers in the notebook or pinned packages. |
| `dependencies` | `dict` | No | `None` | Installed Python distribution names to exact runtime versions. They are checked against installed package metadata; missing/mismatched or unsupported dependency identities prevent successful Testing evidence. Do not include credentials, paths or physical environment bindings. Supply an explicit empty dict when no additional project dependencies exist; omitted dependency identity cannot qualify as successful Testing evidence. |
| `configuration` | `dict` | No | `None` | Declared behavior-changing transformation settings supplied outside notebook code. Supply {} when none exist. Missing identity prevents successful Testing; Live must supply the exact tested values. Exclude secrets and physical bindings. |
| `deployment_path` | `str` | No | `None` | Explicit shared mounted deployment directory containing approved.json, executable.bin and verified deployment.json. Required for Live. |
| `activated_pipeline_id` | `str` | No | `None` | Exact approved version to persist as the environment's Live selection. Omit on subsequent manual/scheduled Live runs to reuse the saved selection. |
| `replace_selection` | `bool` | No | `False` | Explicitly replace a different saved version after verifying its deployment. |

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
    Live selection, manifest, executable/dependency or deployment-binding mismatches.
RuntimeError
    For ambiguous active versions, metadata-read failure, or edits to a built plan.

### Common failure causes

- Bootstrap would bypass a frozen or active contract.
- Missing notebook identity or explicit participant configuration.
- Ambiguous active versions.
- Invalid or mismatched frozen JSON.
- Live is missing an exact Activated Pipeline, verified deployment or saved selection.

## See also

No related guides documented.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/pipeline/setup_pipeline.py:130`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline/setup_pipeline.py#L130-L418">View on GitHub</a>
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

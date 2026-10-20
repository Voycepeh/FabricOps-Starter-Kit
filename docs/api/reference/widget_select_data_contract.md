# `widget_select_data_contract`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview reference-lifecycle-chip-prominent">Preview</span>
</p>

> This function is available for evaluation but is not part of the supported Live release contract. It may change without backward-compatibility guarantees.

Select pipeline-wide Testing/Live and inspect exact frozen contracts per explicit participant.


## Usage notes

Use before Read, including first-time bootstrap without historical Lineage.


## Example usage

<div class="reference-example-usage" markdown="1">

```python
selection = widget_select_data_contract(sources=PIPELINE_SOURCES, targets=PIPELINE_TARGETS)
plan = selection["build_plan"]()
```

</div>

<details class="reference-signature-details" markdown="1">
<summary>Signature</summary>

## Signature

<div class="reference-api-definition" markdown="1">

```python
def widget_select_data_contract(*, sources, targets, spark_session=None, context=None)
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
| `spark_session` | `object` | No | `None` | Spark session for metadata reads. |
| `context` | `dict` | No | `None` | Configured environment routing and notebook identity. |

</div>

## Returns

dict
    Interactive state with execution_mode (initially testing), tables, controls,
    select_contract, set_mode, build_plan and refresh. Each table starts unselected.
    After executing the built plan, refresh shows its exact-version results
    in expandable sections alongside saved definitions and disabled states.
    Explicitly select No Contract for bootstrap; build_plan validates every
    choice and freezes the plan to pass to all Read and Write calls.
    UI edits after build_plan require a new plan and a new run of Read/Transform/Write.
    The widget never changes notebook globals, edits or activates contracts.

### Return interpretation

Select every contract or explicit No Contract, then call build_plan() and pass the same immutable plan to every Read and Write.

## Raises / Errors

ValueError
    For missing notebook identity, invalid payloads, unavailable selections or
    Live choices bypassing an active contract.
RuntimeError
    For ambiguous active versions or a metadata-read failure.

### Common failure causes

- Missing notebook identity or explicit participant configuration.
- Ambiguous active versions.
- Invalid or mismatched frozen JSON.
- Live attempts to bypass an active frozen contract.

## See also

No related guides documented.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/widgets/widget_select_data_contract.py:130`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/widgets/widget_select_data_contract.py#L130-L354">View on GitHub</a>
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

### Release history

| Status | Version |
| --- | --- |
| Preview | 0.2.0 |
| Preview | 0.2.5 |


</details>

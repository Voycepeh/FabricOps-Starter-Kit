# `widget_activate_data_contract`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview reference-lifecycle-chip-prominent">Preview</span>
</p>

> This function is available for evaluation but is not part of the supported Live release contract. It may change without backward-compatibility guarantees.

Link an exact Data Agreement version and activate one validated frozen Data Contract for Production.


## Usage notes

Use after Engineering validates an exact frozen Data Contract version and Governance is ready to activate it for Production.


## Example usage

<div class="reference-example-usage" markdown="1">

```python
state = widget_activate_data_contract(spark_session=spark)
```

</div>

<details class="reference-signature-details" markdown="1">
<summary>Signature</summary>

## Signature

<div class="reference-api-definition" markdown="1">

```python
def widget_activate_data_contract(
    *,
    table_id: str | None=None,
    contract_version: int | None=None,
    spark_session: Any=None,
    context: Any=None,
) -> dict[str, Any]:
```

</div>

</details>

## Parameters

Required describes the Python signature. An optional parameter may still be needed for the selected mode or identity form; see its description. `—` means no signature default.

<div class="reference-input-table" markdown="1">

| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `table_id` | `str \| None` | No | `None` | Initial governed table selection; omitted or unavailable IDs select the first table with a frozen contract. |
| `contract_version` | `int \| None` | No | `None` | Initial frozen version selection. Choose an available version in the UI. |
| `spark_session` | `Any` | No | `None` | Active Fabric Spark session override. |
| `context` | `Any` | No | `None` | FabricOps runtime context established by 00_env_config. |

</div>

## Returns

dict[str, Any]
    Rendered widget, selectors, validation state, activation action, and
    ``refresh`` callback. Opening the widget does not activate a version.

### Return interpretation

The returned state identifies the selected frozen contract and Data Agreement version plus the exact validation evidence used by the activation gate.

## Raises / Errors

ValueError
    If an activation request fails validation. Select a frozen version with
    successful latest Engineering validation and an eligible Data Agreement.
RuntimeError
    If metadata routing, reads, or activation persistence fail. Check the
    configured metadata target and permissions. UI callbacks display failures.

### Common failure causes

- No frozen contract exists for the selected table.
- The exact frozen version has no successful Engineering validation evidence.
- No Data Agreement version is selected.
- The metadata target cannot be read or written.

## Behavior and scope

<div class="reference-docstring-intro" markdown="1">

Only frozen versions are selectable. The exact selected version must have a
successful latest completed Engineering validation run in METADATA_GUARDRAIL_RESULTS
with execution_type='validate' before activation is enabled. The completion
record is written for each participating source and target only after all
checks and Guardrail Coverage pass; isolated or partial check results do not qualify. Activation
links one exact Data Agreement version and updates the active Production
contract pointer; it never edits the immutable contract payload or deploys
the Engineering pipeline.

</div>

## See also

No related guides documented.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/widgets/widget_activate_data_contract.py:81`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/widgets/widget_activate_data_contract.py#L81-L449">View on GitHub</a>
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

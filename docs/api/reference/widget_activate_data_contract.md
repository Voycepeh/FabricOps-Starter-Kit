# `widget_activate_data_contract`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview reference-lifecycle-chip-prominent">Preview</span>
</p>

> This function is available for evaluation but is not part of the supported Live release contract. It may change without backward-compatibility guarantees.

Review exact Testing diagnostics and activate a frozen Data Contract for Live.


## Usage notes

Use for separate Governance approval after reviewing a complete in-memory Testing report.


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
    testing_results: list[dict[str, Any]] | None=None,
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
| `testing_results` | `list[dict[str, Any]] \| None` | No | `None` | Complete Write diagnostics returned by Testing. Only exact payload matches with validation_passed=True qualify for explicit Governance review. Reports remain in memory; opening this widget performs no persistence. |
| `spark_session` | `Any` | No | `None` | Active Fabric Spark session override. |
| `context` | `Any` | No | `None` | FabricOps runtime context established by 00_env_config. |

</div>

## Returns

dict[str, Any]
    Rendered widget, selectors, validation state, activation action, and
    ``refresh`` callback. Opening the widget does not activate a version.

### Return interpretation

Diagnostics qualify a version for explicit Governance review; the separate confirmed activation action mutates governance state.

## Raises / Errors

ValueError
    If an activation request fails validation. Select a frozen version with
    successful Testing diagnostics, explicit review and an eligible Data Agreement.
RuntimeError
    If metadata routing, reads, or activation persistence fail. Check the
    configured metadata target and permissions. UI callbacks display failures.

### Common failure causes

- No eligible frozen version.
- Missing or mismatched Testing report.
- Governance review not approved or no Data Agreement selected.
- Metadata routing or persistence failure.

## Behavior and scope

<div class="reference-docstring-intro" markdown="1">

This separate Governance action requires a successful in-memory Testing
report matching the exact frozen payload, explicit review approval, an exact
Data Agreement version and confirmation. Testing does not register activation
evidence or authorize activation. The approval is a deliberate Governance
decision after reviewing diagnostics and the checks that were not exercised.
Activation never edits the immutable payload or deploys the pipeline.

</div>

## See also

No related guides documented.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/widgets/widget_activate_data_contract.py:43`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/widgets/widget_activate_data_contract.py#L43-L397">View on GitHub</a>
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

# `widget_activate_data_contract`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-discontinued reference-lifecycle-chip-prominent">Discontinued</span>
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-discontinued reference-lifecycle-chip-prominent">Discontinued in 0.3.0</span>
</p>

> This function is no longer part of the current supported public contract. Use the release history below to identify the last supported version.

Review and activate an exact frozen Contract in its physical workspace.



## Example usage

<div class="reference-example-usage" markdown="1">

```python
ui = widget_activate_data_contract(TABLE_ID, CONTRACT_ID, 1)
```

</div>

<details class="reference-signature-details" markdown="1">
<summary>Signature</summary>

## Signature

<div class="reference-api-definition" markdown="1">

```python
def widget_activate_data_contract(
    table_id: str,
    contract_id: str,
    contract_version: int,
    *,
    workspace_id: str | None=None,
    context=None,
) -> dict:
```

</div>

</details>

## Parameters

Required describes the Python signature. An optional parameter may still be needed for the selected mode or identity form; see its description. `—` means no signature default.

<div class="reference-input-table" markdown="1">

| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `table_id` | `str` | Yes | `—` | Exact logical table and frozen Contract identity. |
| `contract_id` | `str` | Yes | `—` | Not documented yet |
| `contract_version` | `int` | Yes | `—` | Exact positive frozen version. |
| `workspace_id` | `str \| None` | No | `None` | Physical table workspace to review; defaults to the configured scope. Use this when reviewing Engineering tables from the Governance notebook. |
| `context` | `dict \| None` | No | `None` | Configured notebook context; central Metadata routing is preserved. |

</div>

## Returns

dict
    Widget, state, confirmation control and activation action. Opening the
    widget changes no metadata. Stale review is rejected atomically.

## Raises / Errors

ValueError
    If the exact frozen Contract, workspace or activation is ambiguous.
RuntimeError
    If configured metadata, Spark or widgets are unavailable.

## Notes

<div class="reference-docstring-notes" markdown="1">

Actual storage permissions authorize activation. The confirmation checkbox
grants no access. Ungoverned writes to the physical table and aliases become
protected; Pipeline Promotion remains a separate decision.

</div>

## See also

No related guides documented.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/widgets/widget_activate_data_contract.py:15`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/widgets/widget_activate_data_contract.py#L15-L106">View on GitHub</a>
</div>


<details class="reference-implementation-details" markdown="1">
<summary>Maintainer architecture details</summary>

## Contract impact

| Property | Value |
| --- | --- |
| Lifecycle | <span class="reference-chip reference-lifecycle-chip reference-lifecycle-discontinued">Discontinued</span> |
| Live since | — |
| Discontinued in | 0.3.0 |
| Contract classification | Discontinued public function |
| Contract risk | Discontinued |
| Live-critical dependencies | 0 |

### Release history

| Status | Version |
| --- | --- |
| Preview | 0.2.0 |
| Preview | 0.2.5 |
| Discontinued | 0.3.0 |
| Discontinued | 0.3.1 |


</details>

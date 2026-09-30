# `widget_activate_data_contract`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview reference-lifecycle-chip-prominent">Preview</span>
<span class="reference-chip reference-chip-muted">Public function</span>
</p>

> This function is available for evaluation but is not part of the supported Live release contract. It may change without backward-compatibility guarantees.

Link an exact Data Agreement version and activate one validated frozen Data Contract for Production.

<div class="reference-docstring-intro" markdown="1">

Only frozen versions are selectable. The exact selected version must have a
successful latest Engineering validation run in METADATA_GUARDRAIL_RESULTS
with execution_type='validate' before activation is enabled. Activation
links one exact Data Agreement version and updates the active Production
contract pointer; it never edits the immutable contract payload or deploys
the Engineering pipeline.

</div>

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/widgets/widget_activate_data_contract.py:68`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/widgets/widget_activate_data_contract.py#L68-L401">View on GitHub</a>
</div>

<p class="reference-catalogue-item-meta reference-catalogue-item-badges">
<span class="reference-chip">Public Starter Kit function</span>
<span class="reference-chip">Usage detection may exclude indirect or generated references.</span>
</p>

**Used in notebooks:** Usage detection may exclude indirect or generated references.

## Usage notes

Widget helpers provide a front-end notebook interface so users can enter metadata in a guided way.

They help users write values into the correct underlying metadata tables without manually editing those tables directly.


## Signature

<div class="reference-api-definition" markdown="1">

```python
def widget_activate_data_contract(
    table_id: str | None=None,
    contract_version: int | None=None,
    spark_session: Any=None,
    context: Any=None,
) -> dict[str, Any]:
```

</div>

## Example usage

Example usage not documented yet.

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `table_id` | `str \| None` | No | Not documented yet |
| `contract_version` | `int \| None` | No | Not documented yet |
| `spark_session` | `Any` | No | Not documented yet |
| `context` | `Any` | No | Not documented yet |

## Returns

Activation state, selected immutable identities, validation evidence, the displayed UI, and the activation result.

### Return interpretation

The returned state identifies the selected frozen contract and Data Agreement version plus the exact validation evidence used by the activation gate.

## Raises / Errors

Raises widget, Spark, configured metadata routing, validation evidence, or contract activation errors.

### Common failure causes

- No frozen contract exists for the selected table.
- The exact frozen version has no successful Engineering validation evidence.
- No Data Agreement version is selected.
- The metadata target cannot be read or written.

## See also

No related guides documented.


<details>
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


</details>

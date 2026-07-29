# `widget_render_data_agreement`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview reference-lifecycle-chip-prominent">Preview</span>
<span class="reference-chip reference-chip-muted">Public function</span>
</p>

> This function is available for evaluation but is not part of the supported Live release contract. It may change without backward-compatibility guarantees.

Render the standalone data-agreement intake widget.

<div class="reference-docstring-intro" markdown="1">

The editor caches active data stewards, keeps one in-memory draft, and
appends one complete agreement row only after final validation.

</div>

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/widgets/widget_render_data_agreement.py:36`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/widgets/widget_render_data_agreement.py#L36-L341">View on GitHub</a>
</div>

<p class="reference-catalogue-item-meta reference-catalogue-item-badges">
<span class="reference-chip">Public Starter Kit function</span>
<span class="reference-chip">01_agreement</span>
</p>

**Used in notebooks:** `01_agreement`

## Usage notes

Widget helpers provide a front-end notebook interface so users can enter metadata in a guided way.

They help users write values into the correct underlying metadata tables without manually editing those tables directly.


## Signature

<div class="reference-api-definition" markdown="1">

```python
def widget_render_data_agreement(
    spark: Any,
    context: dict[str, Any] | None=None,
) -> dict[str, Any]:
```

</div>

## Example usage

Example usage not documented yet.

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `spark` | `Any` | Yes | Fabric Spark session used for initial metadata reads, explicit steward refreshes, and the final append-only write. |
| `context` | `dict[str, Any] \| None` | No | Advanced override for the active Fabric context. When omitted, the helper uses ``FABRIC_CONTEXT`` initialized by ``00_env_config``. |

## Returns

Notebook widget state or rendered widget result used to save agreement details to METADATA_DATA_AGREEMENT.

### Return interpretation

The rendered widget collects agreement input; downstream helpers can only use the agreement after the user saves valid values.

## Raises / Errors

Raises widget, validation, or metadata routing errors when required agreement fields are missing or the metadata table cannot be written.

### Common failure causes

- ipywidgets is not available in the runtime.
- Required agreement fields are missing.
- Agreement identifiers conflict with existing metadata.
- The metadata target cannot be written.

## See also

- [Templates](../../notebook-templates.md)


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
| Preview | 0.1.0 |


</details>

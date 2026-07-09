# `widget_render_data_agreement`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview reference-lifecycle-chip-prominent">Preview</span>
<span class="reference-chip reference-chip-muted">Public function</span>
</p>

> This function is available for evaluation but is not part of the supported Live release contract. It may change without backward-compatibility guarantees.

## Call-flow summary

- Downstream callables: 187
- Shared helpers: 107
- Private helpers: 80

<a class="reference-source-link" href="../../../assets/public-function-call-flows-dashboard.html?function=widget_render_data_agreement">Open Preview call flow</a>

## Contract impact

| Property | Value |
| --- | --- |
| Lifecycle | <span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview">Preview</span> |
| Live since | — |
| Discontinued in | — |
| Contract classification | Preview public function |
| Contract risk | Preview |
| Live-critical dependencies | 0 |


Render the standalone data-agreement intake widget.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/widgets/widget_render_data_agreement.py:34`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/widgets/widget_render_data_agreement.py#L34-L182">View on GitHub</a>
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
| `spark` | `Any` | Yes | Fabric Spark session used for metadata reads and append-only writes. |
| `context` | `dict[str, Any] \| None` | No | Advanced override for the active Fabric context. When omitted, the helper uses ``FABRIC_CONTEXT`` initialized by ``00_env_config``. |

## Returns

dict[str, Any]
    Rendered controls, including read-only generated-identifier context.

### Return interpretation

The rendered widget collects agreement input; downstream helpers can only use the agreement after the user saves valid values.

## Raises / Errors

Not documented yet

### Common failure causes

- ipywidgets is not available in the runtime.
- Required agreement fields are missing.
- Agreement identifiers conflict with existing metadata.
- The metadata target cannot be written.

## See also

- [Notebook Templates Implementation Guide](../../notebook-templates-implementation-guide/index.md)


!!! info "Generated reference freshness"
    Reference pages generated: 09 Jul 2026, 11:26 PM SGT
    Call-flow data generated: 09 Jul 2026, 8:52 PM SGT

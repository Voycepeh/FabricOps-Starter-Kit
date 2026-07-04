# widget_render_data_steward

## Call-flow summary

- Downstream callables: 238
- Shared helpers: 114
- Private helpers: 124

<a class="reference-source-link" href="../../assets/public-function-call-flows-dashboard.html?function=widget_render_data_steward">Open focused call flow in dashboard</a>


Render the standalone data-steward intake widget.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/widgets/widget_render_data_steward.py:11`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/widgets/widget_render_data_steward.py#L11-L29">View on GitHub</a>
</div>

<p class="reference-catalogue-item-meta reference-catalogue-item-badges">
<span class="reference-chip">Public Starter Kit function</span>
<span class="reference-chip">01_agreement</span>
</p>

**Used in notebooks:** `01_agreement`

## Usage notes

Use in 01_agreement when collecting or updating data steward details before creating a data agreement.

Renders the data steward intake widget so a notebook user can capture steward contact and ownership details for an agreement workflow.


## Signature

<div class="reference-api-definition" markdown="1">

```python
def widget_render_data_steward(
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
    Rendered widget controls keyed for notebook customization.

### Return interpretation

The widget itself is the user interface; saved steward values are available to downstream agreement evidence only after the user completes the widget action.

## Raises / Errors

Not documented yet

### Common failure causes

- ipywidgets is not available in the runtime.
- Required steward fields are left blank.
- Widget state is cleared by rerunning cells out of order.
- Metadata routing is unavailable when the widget tries to persist records.

## See also

- [Notebook Templates Implementation Guide](../../notebook-templates-implementation-guide/index.md)

# `widget_render_data_steward`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-live reference-lifecycle-chip-prominent">Live</span>
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-live reference-lifecycle-chip-prominent">Live since 0.2.0</span>
</p>

> This function is part of the supported FabricOps public contract. Changes to its signature, behaviour, public export, or Live-critical dependencies require Live-contract review.

Render the standalone data-steward intake widget.

<p class="reference-catalogue-item-meta reference-catalogue-item-badges">
<span class="reference-chip">01_governance</span>
</p>

## Usage notes

Use in 01_governance when collecting or updating data steward details before creating a data agreement.


## Example usage

<div class="reference-example-usage" markdown="1">

```python
state = widget_render_data_steward(spark=spark)
```

</div>

<details class="reference-signature-details" markdown="1">
<summary>Signature</summary>

## Signature

<div class="reference-api-definition" markdown="1">

```python
def widget_render_data_steward(
    *,
    spark: Any,
    context: dict[str, Any] | None=None,
) -> dict[str, Any]:
```

</div>

</details>

## Parameters

Required describes the Python signature. An optional parameter may still be needed for the selected mode or identity form; see its description. `—` means no signature default.

<div class="reference-input-table" markdown="1">

| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `spark` | `Any` | Yes | `—` | Fabric Spark session used for metadata reads and append-only writes. |
| `context` | `dict[str, Any] \| None` | No | `None` | Advanced override for the active Fabric context. When omitted, the helper uses ``FABRIC_CONTEXT`` initialized by ``00_env_config``. |

</div>

## Returns

dict[str, Any]
    Rendered widget controls keyed for notebook customization.

### Return interpretation

The widget itself is the user interface; saved steward values are available to downstream agreement workflows only after the user completes the widget action.

## Raises / Errors

ValueError
    If required authored fields are invalid. Complete the highlighted fields
    before saving. Widget callbacks display validation failures.
RuntimeError
    If configured metadata routing or persistence fails; check the Metadata
    store configuration and write permissions.

### Common failure causes

- ipywidgets is not available in the runtime.
- Required steward fields are left blank.
- Widget state is cleared by rerunning cells out of order.
- Metadata routing is unavailable when the widget tries to persist records.

## See also

- [Templates](https://github.com/Voycepeh/FabricOps-Starter-Kit/tree/main/templates/notebooks)

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/widgets/widget_render_data_steward.py:35`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/widgets/widget_render_data_steward.py#L35-L218">View on GitHub</a>
</div>


<details class="reference-implementation-details" markdown="1">
<summary>Maintainer architecture details</summary>

## Contract impact

| Property | Value |
| --- | --- |
| Lifecycle | <span class="reference-chip reference-lifecycle-chip reference-lifecycle-live">Live</span> |
| Live since | 0.2.0 |
| Discontinued in | — |
| Contract classification | Live public function |
| Contract risk | Live |
| Live-critical dependencies | 47 |

### Release history

| Status | Version |
| --- | --- |
| Preview | 0.1.0 |
| Live | 0.2.0 |
| Live | 0.2.5 |

### Live-critical dependencies

<ul class="reference-compact-list">
<li><code>fabricops_kit.config.audit._audit_timestamp_value</code></li>
<li><code>fabricops_kit.config.audit._context_get</code></li>
<li><code>fabricops_kit.config.audit._require_audit_values</code></li>
<li><code>fabricops_kit.config.audit._valid_audit_value</code></li>
<li><code>fabricops_kit.config.audit.build_runtime_audit_fields</code></li>
<li><code>fabricops_kit.config.metadata_schemas._coerce_metadata_value</code></li>
<li><code>fabricops_kit.config.metadata_schemas.audit_schema_fields</code></li>
<li><code>fabricops_kit.config.metadata_schemas.build_metadata_schema</code></li>
<li><code>fabricops_kit.config.metadata_schemas.coerce_metadata_row_types</code></li>
<li><code>fabricops_kit.config.metadata_schemas.metadata_table_owner</code></li>
<li><code>fabricops_kit.config.metadata_schemas.metadata_table_physical_schema</code></li>
<li><code>fabricops_kit.config.metadata_schemas.metadata_table_schema_registry</code></li>
<li><code>fabricops_kit.config.shared._normalize_path_config</code></li>
<li><code>fabricops_kit.config.shared._validate_audit_timezone</code></li>
<li><code>fabricops_kit.config.shared.get_audit_timezone</code></li>
<li><code>fabricops_kit.config.shared.get_current_audit_timestamp</code></li>
<li><code>fabricops_kit.config.shared.get_default_fabric_context</code></li>
<li><code>fabricops_kit.config.shared.get_store</code></li>
<li><code>fabricops_kit.config.shared.metadata_timestamp_sort_key</code></li>
<li><code>fabricops_kit.config.shared.normalize_audit_datetime</code></li>
<li><code>fabricops_kit.config.shared.resolve_fabric_context</code></li>
<li><code>fabricops_kit.config.shared.resolve_runtime_context</code></li>
<li><code>fabricops_kit.widgets.shared._coerce_row_dicts</code></li>
<li><code>fabricops_kit.widgets.shared._html_escape</code></li>
<li><code>fabricops_kit.widgets.shared._latest_by_key</code></li>
<li><code>fabricops_kit.widgets.shared.action_row</code></li>
<li><code>fabricops_kit.widgets.shared.active_steward</code></li>
<li><code>fabricops_kit.widgets.shared.collect_custom_fields</code></li>
<li><code>fabricops_kit.widgets.shared.config_value</code></li>
<li><code>fabricops_kit.widgets.shared.deserialize_custom_fields</code></li>
<li><code>fabricops_kit.widgets.shared.form_grid</code></li>
<li><code>fabricops_kit.widgets.shared.form_page</code></li>
<li><code>fabricops_kit.widgets.shared.form_section</code></li>
<li><code>fabricops_kit.widgets.shared.get_widget_visible_fields</code></li>
<li><code>fabricops_kit.widgets.shared.list_data_stewards</code></li>
<li><code>fabricops_kit.widgets.shared.render_custom_fields</code></li>
<li><code>fabricops_kit.widgets.shared.render_searchable_selector</code></li>
<li><code>fabricops_kit.widgets.shared.require_ipywidgets</code></li>
<li><code>fabricops_kit.widgets.shared.serialize_custom_fields</code></li>
<li><code>fabricops_kit.widgets.shared.standard_widget</code></li>
<li><code>fabricops_kit.widgets.shared.status_message</code></li>
<li><code>fabricops_kit.widgets.shared.to_bool</code></li>
<li><code>fabricops_kit.widgets.shared.to_iso_date</code></li>
<li><code>fabricops_kit.widgets.shared.widget_common</code></li>
<li><code>fabricops_kit.widgets.shared.write_widget_metadata_row</code></li>
<li><code>fabricops_kit.widgets.widget_render_data_steward._create_or_update_data_steward</code></li>
<li><code>fabricops_kit.widgets.widget_render_data_steward._generate_steward_id</code></li>
</ul>


</details>

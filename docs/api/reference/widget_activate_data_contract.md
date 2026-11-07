# `widget_activate_data_contract`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-live reference-lifecycle-chip-prominent">Live</span>
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-live reference-lifecycle-chip-prominent">Live since 0.4.0</span>
</p>

> This function is part of the supported FabricOps public contract. Changes to its signature, behaviour, public export, or Live-critical dependencies require Live-contract review.

Review and activate an exact frozen Contract in its physical workspace.


## Usage notes

Use after widget_data_contract freezes a version to activate it for a physical table and workspace.


## Example usage

<div class="reference-example-usage" markdown="1">

```python
ui = widget_activate_data_contract()
ui = widget_activate_data_contract(TABLE_ID, CONTRACT_ID, 1,
    workspace_id=PHYSICAL_WORKSPACE_ID)
```

</div>

<details class="reference-signature-details" markdown="1">
<summary>Signature</summary>

## Signature

<div class="reference-api-definition" markdown="1">

```python
def widget_activate_data_contract(
    table_id: str | None=None,
    contract_id: str | None=None,
    contract_version: int | None=None,
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
| `table_id` | `str \| None` | No | `None` | Preselect an exact logical table and frozen Contract. With no arguments, select from registered physical workspaces/tables and frozen versions. |
| `contract_id` | `str \| None` | No | `None` | Not documented yet |
| `contract_version` | `int \| None` | No | `None` | Exact positive frozen version to preselect; never a latest fallback. |
| `workspace_id` | `str \| None` | No | `None` | Physical table workspace. With a supplied table, defaults to the current configured scope. Governance metadata stays in its central Lakehouse. |
| `context` | `dict \| None` | No | `None` | Configured Governance notebook context. |

</div>

## Returns

dict
    Widget, selection/review state, controls and review/activate/refresh actions.
    Opening changes no metadata. Backend mutation independently revalidates
    exact bindings, policy hashes and the reviewed current activation ID.

## Raises / Errors

Not documented yet

## Notes

<div class="reference-docstring-notes" markdown="1">

Governance owns all central metadata, so selection uses Catalogue records
without opening Engineering workspaces. Actual Fabric permissions authorize
writes. Each physical activation selects one frozen Contract and at most one
Agreement; cross-workspace execution requires effective associated terms.
Retained revisions provide history independently of notebook promotion.

</div>

## See also

No related guides documented.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/widgets/widget_activate_data_contract.py:18`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/widgets/widget_activate_data_contract.py#L18-L202">View on GitHub</a>
</div>


<details class="reference-implementation-details" markdown="1">
<summary>Maintainer architecture details</summary>

## Contract impact

| Property | Value |
| --- | --- |
| Lifecycle | <span class="reference-chip reference-lifecycle-chip reference-lifecycle-live">Live</span> |
| Live since | 0.4.0 |
| Discontinued in | 0.3.0 |
| Contract classification | Live public function |
| Contract risk | Live |
| Live-critical dependencies | 67 |

### Release history

| Status | Version |
| --- | --- |
| Preview | 0.2.0 |
| Preview | 0.2.5 |
| Discontinued | 0.3.0 |
| Discontinued | 0.3.1 |
| Live | 0.4.0 |
| Live | 0.4.1 |

### Live-critical dependencies

<ul class="reference-compact-list">
<li><code>fabricops_kit.activated_pipeline.shared.activation_operations</code></li>
<li><code>fabricops_kit.activated_pipeline.shared.agreement_definition</code></li>
<li><code>fabricops_kit.activated_pipeline.shared.check_contract_agreement</code></li>
<li><code>fabricops_kit.activated_pipeline.shared.exact_record</code></li>
<li><code>fabricops_kit.activated_pipeline.shared.manifest_digest</code></li>
<li><code>fabricops_kit.activated_pipeline.shared.metadata_path</code></li>
<li><code>fabricops_kit.activated_pipeline.shared.metadata_records</code></li>
<li><code>fabricops_kit.activated_pipeline.shared.mutate_metadata</code></li>
<li><code>fabricops_kit.activated_pipeline.shared.normalized_destination</code></li>
<li><code>fabricops_kit.activated_pipeline.shared.read_activation_history</code></li>
<li><code>fabricops_kit.activated_pipeline.shared.replace_metadata_transaction</code></li>
<li><code>fabricops_kit.activated_pipeline.shared.set_table_contract_activation</code></li>
<li><code>fabricops_kit.activated_pipeline.shared.validate_activations</code></li>
<li><code>fabricops_kit.activated_pipeline.shared.validate_agreement</code></li>
<li><code>fabricops_kit.activated_pipeline.shared.validate_registry</code></li>
<li><code>fabricops_kit.config.audit._audit_timestamp_value</code></li>
<li><code>fabricops_kit.config.audit._context_get</code></li>
<li><code>fabricops_kit.config.audit._require_audit_values</code></li>
<li><code>fabricops_kit.config.audit._valid_audit_value</code></li>
<li><code>fabricops_kit.config.audit.build_runtime_audit_fields</code></li>
<li><code>fabricops_kit.config.metadata_schemas._coerce_metadata_field</code></li>
<li><code>fabricops_kit.config.metadata_schemas._coerce_metadata_value</code></li>
<li><code>fabricops_kit.config.metadata_schemas.audit_schema_fields</code></li>
<li><code>fabricops_kit.config.metadata_schemas.build_metadata_schema</code></li>
<li><code>fabricops_kit.config.metadata_schemas.coerce_metadata_row_types</code></li>
<li><code>fabricops_kit.config.metadata_schemas.decode_metadata_row</code></li>
<li><code>fabricops_kit.config.metadata_schemas.metadata_json_schema</code></li>
<li><code>fabricops_kit.config.metadata_schemas.metadata_schema_type_name</code></li>
<li><code>fabricops_kit.config.metadata_schemas.metadata_table_owner</code></li>
<li><code>fabricops_kit.config.metadata_schemas.metadata_table_physical_schema</code></li>
<li><code>fabricops_kit.config.metadata_schemas.metadata_table_schema_registry</code></li>
<li><code>fabricops_kit.config.metadata_schemas.parse_metadata_json</code></li>
<li><code>fabricops_kit.config.metadata_schemas.validate_metadata_value</code></li>
<li><code>fabricops_kit.config.shared._get_fabric_runtime_context</code></li>
<li><code>fabricops_kit.config.shared._get_fabric_runtime_metadata</code></li>
<li><code>fabricops_kit.config.shared._normalize_path_config</code></li>
<li><code>fabricops_kit.config.shared._validate_audit_timezone</code></li>
<li><code>fabricops_kit.config.shared.get_audit_timezone</code></li>
<li><code>fabricops_kit.config.shared.get_current_audit_timestamp</code></li>
<li><code>fabricops_kit.config.shared.get_default_fabric_context</code></li>
<li><code>fabricops_kit.config.shared.get_store</code></li>
<li><code>fabricops_kit.config.shared.normalize_audit_datetime</code></li>
<li><code>fabricops_kit.config.shared.resolve_fabric_context</code></li>
<li><code>fabricops_kit.config.shared.resolve_runtime_context</code></li>
<li><code>fabricops_kit.io.shared._join_lakehouse_area_path</code></li>
<li><code>fabricops_kit.io.shared._normalize_schema_name</code></li>
<li><code>fabricops_kit.io.shared._normalize_table_name</code></li>
<li><code>fabricops_kit.io.shared._resolve_lakehouse_schema</code></li>
<li><code>fabricops_kit.io.shared._resolve_lakehouse_table_path</code></li>
<li><code>fabricops_kit.io.shared._validate_lakehouse_store</code></li>
<li><code>fabricops_kit.io.shared._validate_warehouse_store</code></li>
<li><code>fabricops_kit.io.shared.get_spark_session</code></li>
<li><code>fabricops_kit.io.shared.resolve_configured_lakehouse_table</code></li>
<li><code>fabricops_kit.io.shared.resolve_lakehouse_table_location</code></li>
<li><code>fabricops_kit.io.shared.resolve_store</code></li>
<li><code>fabricops_kit.io.shared.retry_delta_metadata</code></li>
<li><code>fabricops_kit.pipeline.shared._row_to_dict</code></li>
<li><code>fabricops_kit.pipeline.shared.canonical_pipeline_json</code></li>
<li><code>fabricops_kit.pipeline.shared.pipeline_physical_bindings</code></li>
<li><code>fabricops_kit.pipeline.shared.pipeline_record_content</code></li>
<li><code>fabricops_kit.pipeline.shared.resolve_catalogue_table_identity</code></li>
<li><code>fabricops_kit.pipeline.shared.validate_pipeline_id</code></li>
<li><code>fabricops_kit.pipeline.shared.validate_pipeline_run</code></li>
<li><code>fabricops_kit.pipeline.shared.validated_processing</code></li>
<li><code>fabricops_kit.widgets.shared._html_escape</code></li>
<li><code>fabricops_kit.widgets.shared.form_page</code></li>
<li><code>fabricops_kit.widgets.shared.require_ipywidgets</code></li>
</ul>


</details>

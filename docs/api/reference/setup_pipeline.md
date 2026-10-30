# `setup_pipeline`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-live reference-lifecycle-chip-prominent">Live</span>
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-live reference-lifecycle-chip-prominent">Live since 0.3.0</span>
</p>

> This function is part of the supported FabricOps public contract. Changes to its signature, behaviour, public export, or Live-critical dependencies require Live-contract review.

Prepare Testing or resolve an approved workspace configuration for Live.


## Usage notes

Call after setup_notebook() and before Read, Transform and Write. Test registers or recovers the Pipeline ID automatically.


## Example usage

<div class="reference-example-usage" markdown="1">

```python
context = setup_notebook()
pipeline = setup_pipeline(pipeline_id="8f32a471-6c91-4b7e-9d13-2f0c947eab52", pipeline_mode="Ungoverned")
orders = orchestrate_read(store="Bronze", schema="demo", table_name="orders")
independent_copy = setup_pipeline(pipeline_mode="Ungoverned", new_pipeline=True)
reuploaded = setup_pipeline(pipeline_id=PIPELINE_ID, pipeline_mode="Ungoverned",
    previous_workspace_id=old_workspace_id, previous_notebook_id=old_notebook_id)
```

</div>

<details class="reference-signature-details" markdown="1">
<summary>Signature</summary>

## Signature

<div class="reference-api-definition" markdown="1">

```python
def setup_pipeline(
    *,
    pipeline_id: str | None=None,
    pipeline_mode: str='Ungoverned',
    new_pipeline: bool=False,
    previous_workspace_id: str | None=None,
    previous_notebook_id: str | None=None,
):
```

</div>

</details>

## Parameters

Required describes the Python signature. An optional parameter may still be needed for the selected mode or identity form; see its description. `—` means no signature default.

<div class="reference-input-table" markdown="1">

| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `pipeline_id` | `str \| None` | No | `None` | Permanent UUIDv4. Omit to recover the exact notebook binding or register a new UUID in Ungoverned mode. Dry Run may use a session-only UUID and never registers it. Governed never allocates a new UUID. A changed same-workspace_id binding requires both previous notebook IDs. |
| `pipeline_mode` | `str` | No | `'Ungoverned'` | Preview without writing, execute without contracts, or execute with activated contracts enforced. |
| `new_pipeline` | `bool` | No | `False` | Explicitly create a new identity for an independent notebook copy. Omit pipeline_id when set. An already registered notebook is rejected. |
| `previous_workspace_id` | `str \| None` | No | `None` | Supply both old binding IDs to explicitly rebind a reuploaded notebook. Rebinding requires Ungoverned mode and no active Governed runs. |
| `previous_notebook_id` | `str \| None` | No | `None` | Not documented yet |

</div>

## Returns

PipelineSession
    Contract selection, pipeline_id containing the permanent UUID, registration
    details and the automatically refreshed execution report. Read and
    Write calls use this execution through a context-local binding.

### Return interpretation

Returns a context-local execution session exposing pipeline_id, contract selection and automatic reporting; finalize_pipeline records completion and commits Test results; interrupted runs remain incomplete.

## Raises / Errors

ValueError
    For an invalid UUIDv4, conflicting notebook binding, unsupported mode or
    missing Governed activation.
RuntimeError
    If setup_notebook() has not completed successfully for the current
    execution, or a Spark session is unavailable.

### Common failure causes

- Missing, failed or outdated setup_notebook() initialization.
- Invalid frozen contract selections.
- Missing notebook registration or approved Live configuration.

## Notes

<div class="reference-docstring-notes" markdown="1">

Call setup_notebook() first to initialize configuration and display notebook
readiness. This function reuses that configuration without rerunning
00_env_config or displaying the workspace_id summary. Cross-workspace
configuration is selected only through setup_notebook(config_workspace_id=...).
Repeated pipeline setup closes the preceding execution owned by this task.
Repeated notebook setup closes its pipeline and invalidates prior configuration,
including when the new setup fails. Changed runtime identity requires fresh
notebook setup.

Fabric cell events identify failures, not successful notebook completion.
Call finalize_pipeline after all Reads, transformations and Writes.
Neither a successful Write nor interpreter shutdown proves completion. Dry
Run finalization returns only a session summary and does not persist it.

</div>

## Behavior and scope

<div class="reference-docstring-intro" markdown="1">

Dry Run evaluates real reads, transformations, profiling and optionally
selected contract Guardrails without persisting target data or operational
state. Ungoverned executes without Data Contracts while retaining operational
checks and blocks writes to tables already governed in the workspace.
Governed resolves only activated workspace authority and enforces its exact
contract versions, destinations and ownership throughout the run.
Spark and supported Fabric runtime identity are resolved internally. The caller workspace and notebook IDs are required for registration.

</div>

## See also

No related guides documented.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/pipeline/setup_pipeline.py:130`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline/setup_pipeline.py#L130-L222">View on GitHub</a>
</div>


<details class="reference-implementation-details" markdown="1">
<summary>Maintainer architecture details</summary>

## Contract impact

| Property | Value |
| --- | --- |
| Lifecycle | <span class="reference-chip reference-lifecycle-chip reference-lifecycle-live">Live</span> |
| Live since | 0.3.0 |
| Discontinued in | — |
| Contract classification | Live public function |
| Contract risk | Live |
| Live-critical dependencies | 88 |

### Release history

| Status | Version |
| --- | --- |
| Live | 0.3.0 |

### Live-critical dependencies

<ul class="reference-compact-list">
<li><code>fabricops_kit.activated_pipeline.shared.activation_impact</code></li>
<li><code>fabricops_kit.activated_pipeline.shared.agreement_definition</code></li>
<li><code>fabricops_kit.activated_pipeline.shared.approval_record</code></li>
<li><code>fabricops_kit.activated_pipeline.shared.authority_records</code></li>
<li><code>fabricops_kit.activated_pipeline.shared.build_live_pipeline_plan</code></li>
<li><code>fabricops_kit.activated_pipeline.shared.commit_pipeline_authority</code></li>
<li><code>fabricops_kit.activated_pipeline.shared.empty_pipeline_authority</code></li>
<li><code>fabricops_kit.activated_pipeline.shared.exact_record</code></li>
<li><code>fabricops_kit.activated_pipeline.shared.manifest_digest</code></li>
<li><code>fabricops_kit.activated_pipeline.shared.metadata_records</code></li>
<li><code>fabricops_kit.activated_pipeline.shared.pipeline_authority_row</code></li>
<li><code>fabricops_kit.activated_pipeline.shared.pipeline_table_mappings</code></li>
<li><code>fabricops_kit.activated_pipeline.shared.read_pipeline_authority</code></li>
<li><code>fabricops_kit.activated_pipeline.shared.release_pipeline_lease</code></li>
<li><code>fabricops_kit.activated_pipeline.shared.run_contracts</code></li>
<li><code>fabricops_kit.activated_pipeline.shared.testing_run_evidence</code></li>
<li><code>fabricops_kit.activated_pipeline.shared.validate_agreement</code></li>
<li><code>fabricops_kit.activated_pipeline.shared.validate_authority_collections</code></li>
<li><code>fabricops_kit.activated_pipeline.shared.verify_live_plan</code></li>
<li><code>fabricops_kit.activated_pipeline.shared.workspace_activation</code></li>
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
<li><code>fabricops_kit.config.metadata_schemas.metadata_schema_type_name</code></li>
<li><code>fabricops_kit.config.metadata_schemas.metadata_table_field_names</code></li>
<li><code>fabricops_kit.config.metadata_schemas.metadata_table_owner</code></li>
<li><code>fabricops_kit.config.metadata_schemas.metadata_table_physical_schema</code></li>
<li><code>fabricops_kit.config.metadata_schemas.metadata_table_schema_registry</code></li>
<li><code>fabricops_kit.config.metadata_schemas.validate_catalogue_value</code></li>
<li><code>fabricops_kit.config.shared._get_fabric_runtime_context</code></li>
<li><code>fabricops_kit.config.shared._get_fabric_runtime_metadata</code></li>
<li><code>fabricops_kit.config.shared._normalize_path_config</code></li>
<li><code>fabricops_kit.config.shared._validate_audit_timezone</code></li>
<li><code>fabricops_kit.config.shared.build_table_id</code></li>
<li><code>fabricops_kit.config.shared.get_audit_timezone</code></li>
<li><code>fabricops_kit.config.shared.get_current_audit_timestamp</code></li>
<li><code>fabricops_kit.config.shared.get_default_fabric_context</code></li>
<li><code>fabricops_kit.config.shared.get_store</code></li>
<li><code>fabricops_kit.config.shared.normalize_audit_datetime</code></li>
<li><code>fabricops_kit.config.shared.resolve_fabric_context</code></li>
<li><code>fabricops_kit.config.shared.resolve_runtime_context</code></li>
<li><code>fabricops_kit.config.shared.stable_metadata_id</code></li>
<li><code>fabricops_kit.io.shared._build_warehouse_object_name</code></li>
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
<li><code>fabricops_kit.io.shared.resolve_warehouse_name</code></li>
<li><code>fabricops_kit.io.shared.resolve_warehouse_table_location</code></li>
<li><code>fabricops_kit.pipeline.shared._contract_payload</code></li>
<li><code>fabricops_kit.pipeline.shared._merge_pipeline_run_row</code></li>
<li><code>fabricops_kit.pipeline.shared._read_pipeline_run_rows</code></li>
<li><code>fabricops_kit.pipeline.shared._row_to_dict</code></li>
<li><code>fabricops_kit.pipeline.shared.canonical_pipeline_json</code></li>
<li><code>fabricops_kit.pipeline.shared.close_current_pipeline_session</code></li>
<li><code>fabricops_kit.pipeline.shared.commit_pipeline_registration</code></li>
<li><code>fabricops_kit.pipeline.shared.contract_guardrail_rows</code></li>
<li><code>fabricops_kit.pipeline.shared.persist_pipeline_run</code></li>
<li><code>fabricops_kit.pipeline.shared.pipeline_physical_bindings</code></li>
<li><code>fabricops_kit.pipeline.shared.pipeline_record_content</code></li>
<li><code>fabricops_kit.pipeline.shared.pipeline_run_row</code></li>
<li><code>fabricops_kit.pipeline.shared.read_pipeline_registry</code></li>
<li><code>fabricops_kit.pipeline.shared.resolve_catalogue_table_identity</code></li>
<li><code>fabricops_kit.pipeline.shared.resolve_physical_table_identity</code></li>
<li><code>fabricops_kit.pipeline.shared.resolve_pipeline_participants</code></li>
<li><code>fabricops_kit.pipeline.shared.resolve_pipeline_registration</code></li>
<li><code>fabricops_kit.pipeline.shared.start_pipeline_session</code></li>
<li><code>fabricops_kit.pipeline.shared.validate_grain_parameters</code></li>
<li><code>fabricops_kit.pipeline.shared.validate_pipeline_id</code></li>
<li><code>fabricops_kit.pipeline.shared.validate_pipeline_registrations</code></li>
<li><code>fabricops_kit.pipeline.shared.validate_pipeline_run</code></li>
<li><code>fabricops_kit.widgets.shared._html_escape</code></li>
<li><code>fabricops_kit.widgets.shared.form_page</code></li>
<li><code>fabricops_kit.widgets.shared.require_ipywidgets</code></li>
</ul>


</details>

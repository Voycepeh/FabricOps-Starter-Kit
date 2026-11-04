# `setup_pipeline`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-live reference-lifecycle-chip-prominent">Live</span>
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-live reference-lifecycle-chip-prominent">Live since 0.3.0</span>
</p>

> This function is part of the supported FabricOps public contract. Changes to its signature, behaviour, public export, or Live-critical dependencies require Live-contract review.

Start Dry Run or explicit-ID Ungoverned execution; Governed fails closed pending signed-in Fabric validation.


## Usage notes

Call after setup_notebook() and before Read, Transform and Write. Persistent execution requires an explicit saved Pipeline ID.


## Example usage

<div class="reference-example-usage" markdown="1">

```python
context = setup_notebook()
pipeline = setup_pipeline(pipeline_id="8f32a471-6c91-4b7e-9d13-2f0c947eab52", pipeline_mode="Ungoverned")
preview = setup_pipeline(pipeline_mode="Dry Run")
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
    observe_source: bool=False,
    source_observation_days: int | None=None,
):
```

</div>

</details>

## Parameters

Required describes the Python signature. An optional parameter may still be needed for the selected mode or identity form; see its description. `—` means no signature default.

<div class="reference-input-table" markdown="1">

| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `pipeline_id` | `str \| None` | No | `None` | Canonical lowercase UUIDv4 kept in version-controlled pipeline source, stable across environments and notebook deployments. Required for Ungoverned and Governed. Dry Run may allocate a session-only ID. |
| `pipeline_mode` | `str` | No | `'Ungoverned'` | Preview, publish without governance, or enforce activated governance. |
| `observe_source` | `bool` | No | `False` | Manually request a full physical Source Observation for this execution. |
| `source_observation_days` | `int \| None` | No | `None` | Automatically observe after this many days since the last accepted full observation. None disables automatic observation. Manual requests override the interval. Incremental SQL scope does not restrict observation. Baselines are accepted only with verified target publication; failed or no-op writes do not consume the interval. Changed fingerprints are diagnostic unless a separately configured Source Drift policy blocks publication. |

</div>

## Returns

PipelineSession
    Context-local Read/Write execution and in-memory report. Call
    finalize_pipeline after every Read, transformation and Write completes.

### Return interpretation

Returns a context-local Dry Run/Ungoverned session exposing the explicit Pipeline ID, optional Dry Run Contract preview and execution reporting. finalize_pipeline records completion; interrupted runs remain incomplete. Governed is blocked pending signed-in Fabric validation.

## Raises / Errors

ValueError
    If the mode or Pipeline ID is invalid, or a persistent ID is omitted.
RuntimeError
    If notebook setup or Spark is unavailable, or signed-in Fabric validation
    remains pending. Governed fails before admission and publication.

### Common failure causes

- Missing, failed or outdated setup_notebook() initialization.
- Invalid frozen contract selections.
- Missing explicit persistent Pipeline ID or pending Governed deployment verification.

## Notes

<div class="reference-docstring-notes" markdown="1">

Call setup_notebook first. Spark and Fabric identity come from that setup.
There is no permanent registration, approval, notebook rebinding or automatic
UUID recovery. A notebook may use different explicit Pipeline IDs. Repeated
setup closes the previous execution. Dry Run never writes Registry, Run,
profiling results or Processing State. Completed captured Dry Runs retain
serializable saved-definition/test claims in Engineering Files for submission.
Persistent runs record final outcomes;
a successful Write does not imply successful whole-notebook completion.

</div>

## Behavior and scope

<div class="reference-docstring-intro" markdown="1">

Dry Run previews transformations, optional Contract checks and profiling without
durable mutations. Ungoverned publishes without activated Contracts, but cannot
write protected Table IDs or physical destination aliases. Governed requires
a promoted notebook and independently activated Contracts for all sources
and targets. It remains fail closed pending signed-in Fabric validation.

</div>

## See also

No related guides documented.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/pipeline/setup_pipeline.py:130`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline/setup_pipeline.py#L130-L210">View on GitHub</a>
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
| Live-critical dependencies | 80 |

### Release history

| Status | Version |
| --- | --- |
| Live | 0.3.0 |
| Live | 0.3.1 |

### Live-critical dependencies

<ul class="reference-compact-list">
<li><code>fabricops_kit.activated_pipeline.shared._strict_package_json</code></li>
<li><code>fabricops_kit.activated_pipeline.shared.activation_operations</code></li>
<li><code>fabricops_kit.activated_pipeline.shared.agreement_definition</code></li>
<li><code>fabricops_kit.activated_pipeline.shared.authoritative_approval</code></li>
<li><code>fabricops_kit.activated_pipeline.shared.build_governed_pipeline_plan</code></li>
<li><code>fabricops_kit.activated_pipeline.shared.check_contract_agreement</code></li>
<li><code>fabricops_kit.activated_pipeline.shared.exact_record</code></li>
<li><code>fabricops_kit.activated_pipeline.shared.manifest_digest</code></li>
<li><code>fabricops_kit.activated_pipeline.shared.metadata_records</code></li>
<li><code>fabricops_kit.activated_pipeline.shared.normalized_destination</code></li>
<li><code>fabricops_kit.activated_pipeline.shared.notebook_executable_digest</code></li>
<li><code>fabricops_kit.activated_pipeline.shared.notebook_implementation_digest</code></li>
<li><code>fabricops_kit.activated_pipeline.shared.promoted_notebook</code></li>
<li><code>fabricops_kit.activated_pipeline.shared.read_activation_history</code></li>
<li><code>fabricops_kit.activated_pipeline.shared.read_activations</code></li>
<li><code>fabricops_kit.activated_pipeline.shared.read_approvals</code></li>
<li><code>fabricops_kit.activated_pipeline.shared.read_registry</code></li>
<li><code>fabricops_kit.activated_pipeline.shared.resolve_activation_contract</code></li>
<li><code>fabricops_kit.activated_pipeline.shared.resolve_promoted_operations</code></li>
<li><code>fabricops_kit.activated_pipeline.shared.reviewed_contracts</code></li>
<li><code>fabricops_kit.activated_pipeline.shared.snapshot_file</code></li>
<li><code>fabricops_kit.activated_pipeline.shared.validate_activations</code></li>
<li><code>fabricops_kit.activated_pipeline.shared.validate_agreement</code></li>
<li><code>fabricops_kit.activated_pipeline.shared.validate_approvals</code></li>
<li><code>fabricops_kit.activated_pipeline.shared.validate_registry</code></li>
<li><code>fabricops_kit.activated_pipeline.shared.validate_submission</code></li>
<li><code>fabricops_kit.activated_pipeline.shared.verify_promotion_integrity</code></li>
<li><code>fabricops_kit.activated_pipeline.shared.verify_registry_approval</code></li>
<li><code>fabricops_kit.config.metadata_schemas.audit_schema_fields</code></li>
<li><code>fabricops_kit.config.metadata_schemas.build_metadata_schema</code></li>
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
<li><code>fabricops_kit.config.shared.build_table_id</code></li>
<li><code>fabricops_kit.config.shared.get_default_fabric_context</code></li>
<li><code>fabricops_kit.config.shared.get_store</code></li>
<li><code>fabricops_kit.config.shared.resolve_fabric_context</code></li>
<li><code>fabricops_kit.config.shared.resolve_runtime_context</code></li>
<li><code>fabricops_kit.config.shared.stable_metadata_id</code></li>
<li><code>fabricops_kit.data_contract.shared.normalize_guardrail_action</code></li>
<li><code>fabricops_kit.data_contract.shared.validate_contract_definitions</code></li>
<li><code>fabricops_kit.data_contract.shared.validate_grain_contract</code></li>
<li><code>fabricops_kit.data_contract.shared.validate_sensitive_data_parameters</code></li>
<li><code>fabricops_kit.io.shared._build_warehouse_object_name</code></li>
<li><code>fabricops_kit.io.shared._join_lakehouse_area_path</code></li>
<li><code>fabricops_kit.io.shared._normalize_schema_name</code></li>
<li><code>fabricops_kit.io.shared._normalize_table_name</code></li>
<li><code>fabricops_kit.io.shared._resolve_lakehouse_schema</code></li>
<li><code>fabricops_kit.io.shared._resolve_lakehouse_table_path</code></li>
<li><code>fabricops_kit.io.shared.get_spark_session</code></li>
<li><code>fabricops_kit.io.shared.resolve_lakehouse_table_location</code></li>
<li><code>fabricops_kit.io.shared.resolve_warehouse_name</code></li>
<li><code>fabricops_kit.io.shared.resolve_warehouse_table_location</code></li>
<li><code>fabricops_kit.pipeline.shared._contract_payload</code></li>
<li><code>fabricops_kit.pipeline.shared._row_to_dict</code></li>
<li><code>fabricops_kit.pipeline.shared.canonical_pipeline_json</code></li>
<li><code>fabricops_kit.pipeline.shared.close_current_pipeline_session</code></li>
<li><code>fabricops_kit.pipeline.shared.contract_guardrail_rows</code></li>
<li><code>fabricops_kit.pipeline.shared.pipeline_physical_bindings</code></li>
<li><code>fabricops_kit.pipeline.shared.pipeline_record_content</code></li>
<li><code>fabricops_kit.pipeline.shared.resolve_catalogue_table_identity</code></li>
<li><code>fabricops_kit.pipeline.shared.resolve_physical_table_identity</code></li>
<li><code>fabricops_kit.pipeline.shared.resolve_pipeline_participants</code></li>
<li><code>fabricops_kit.pipeline.shared.start_pipeline_session</code></li>
<li><code>fabricops_kit.pipeline.shared.validate_grain_parameters</code></li>
<li><code>fabricops_kit.pipeline.shared.validate_pipeline_id</code></li>
<li><code>fabricops_kit.pipeline.shared.validate_pipeline_run</code></li>
<li><code>fabricops_kit.pipeline.shared.validate_profiling_policy</code></li>
<li><code>fabricops_kit.pipeline.shared.validated_processing</code></li>
<li><code>fabricops_kit.widgets.shared._html_escape</code></li>
<li><code>fabricops_kit.widgets.shared.form_page</code></li>
<li><code>fabricops_kit.widgets.shared.require_ipywidgets</code></li>
</ul>


</details>

# `finalize_pipeline`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-live reference-lifecycle-chip-prominent">Live</span>
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-live reference-lifecycle-chip-prominent">Live since 0.3.0</span>
</p>

> This function is part of the supported FabricOps public contract. Changes to its signature, behaviour, public export, or Live-critical dependencies require Live-contract review.

Complete execution or reopen persisted Engineering submission, deployment and recovery controls.

<p class="reference-catalogue-item-meta reference-catalogue-item-badges">
<span class="reference-chip">02_pipeline</span>
<span class="reference-chip">02A_full_refresh_demo</span>
<span class="reference-chip">02B_incremental_append_demo</span>
<span class="reference-chip">02C_scd_demo</span>
</p>

## Usage notes

Call after all Reads, transformations and Writes, including read-only runs.


## Example usage

<div class="reference-example-usage" markdown="1">

```python
pipeline = setup_pipeline(pipeline_mode="Ungoverned")
source = orchestrate_read(store="Bronze", schema="demo", table_name="orders")
pipeline_result = finalize_pipeline(pipeline)
handoff = finalize_pipeline()
```

</div>

<details class="reference-signature-details" markdown="1">
<summary>Signature</summary>

## Signature

<div class="reference-api-definition" markdown="1">

```python
def finalize_pipeline(pipeline=None, *, failed=False)
```

</div>

</details>

## Parameters

Required describes the Python signature. An optional parameter may still be needed for the selected mode or identity form; see its description. `—` means no signature default.

<div class="reference-input-table" markdown="1">

| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `pipeline` | `PipelineSession` | No | `None` | Execution returned by setup_pipeline. Retain it for repeat finalization. |
| `failed` | `bool` | No | `False` | Mark a caught project failure; recorded failures cannot become success. |

</div>

## Returns

dict
    Final execution summary. For persistent modes this is the
    METADATA_PIPELINE_RUN snapshot; Dry Run returns the in-memory equivalent.
    When pipeline Source Drift is enabled, adds a source_drift diagnostic
    summary and separate baseline acceptance status without altering the
    immutable Run record. Failed or unconfirmed baseline acceptance does
    not roll back completed target publications. An unconfirmed outcome
    requires inspection of immutable acceptance history before retrying.
    Each operation retains legacy rows_read/rows_written plus its available
    detailed Read or strategy-specific Write metrics. Missing fields on
    historical records remain valid and display as not captured.
    When no session is active, returns the resolved pipeline_id and handoff
    (the displayed controls and their state/actions), without a Run record.

## Raises / Errors

ValueError
    If pipeline is not a setup_pipeline session or audit identity is missing.
RuntimeError
    If notebook setup is invalid, runtime identity has changed, another task
    owns the execution, or metadata publication fails. Run and Guardrail IDs
    remain stable for supported publication retries.

## Behavior and scope

<div class="reference-docstring-intro" markdown="1">

Call once after all Reads, transformations and Writes, including read-only
runs. Pass the session returned by setup_pipeline, or omit it to use the
current execution. Set failed=True when a project exception was caught.
To reopen persisted approval/deployment/recovery controls after notebook setup
in an independent session, omit the session; FabricOps resolves the current
notebook through the Pipeline Registry. This does not start or finalize a run,
export a new candidate, deploy or repair automatically.
A successful Write or cell never completes the whole pipeline by itself.
Open sessions require the current initialized notebook configuration and
runtime identity, whether passed explicitly or selected implicitly. Already
closed sessions retain their recorded outcome for repeat finalization.

Dry Run returns a session-only summary and persists no target, watermark,
processing state, profile observation or run metadata. A completed captured
Dry Run retains complete saved-definition and test claims in Engineering
Files for independent submission. For a completed captured Dry Run, save a
saved package for direct Governance selection and display its status plus
approval refresh, explicit
deployment and recovery controls below the summary. Repeat finalization on
the retained session to reopen them; it reuses the package and does not
repeat the run or deploy automatically. Presentation/export failures are
reported separately and do not change the finalized outcome. This is not
Governance approval. Ungoverned and
Governed executions persist their real operational outcome. Persistent
finalization records whole-run completion. Interrupted runs remain incomplete
and are never reported as successful finalization. Each target has one owning
pipeline; schedules must prevent overlapping writes to the same target.

</div>

## See also

No related guides documented.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/pipeline/finalize_pipeline.py:192`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline/finalize_pipeline.py#L192-L304">View on GitHub</a>
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
| Live-critical dependencies | 106 |

### Release history

| Status | Version |
| --- | --- |
| Live | 0.3.0 |
| Live | 0.3.1 |
| Live | 0.4.0 |
| Live | 0.4.1 |

### Live-critical dependencies

<ul class="reference-compact-list">
<li><code>fabricops_kit.activated_pipeline.shared._strict_package_json</code></li>
<li><code>fabricops_kit.activated_pipeline.shared.activation_operations</code></li>
<li><code>fabricops_kit.activated_pipeline.shared.agreement_definition</code></li>
<li><code>fabricops_kit.activated_pipeline.shared.authoritative_approval</code></li>
<li><code>fabricops_kit.activated_pipeline.shared.check_contract_agreement</code></li>
<li><code>fabricops_kit.activated_pipeline.shared.commit_pipeline_promotion</code></li>
<li><code>fabricops_kit.activated_pipeline.shared.deploy_approved_submission</code></li>
<li><code>fabricops_kit.activated_pipeline.shared.display_pipeline_handoff</code></li>
<li><code>fabricops_kit.activated_pipeline.shared.exact_record</code></li>
<li><code>fabricops_kit.activated_pipeline.shared.export_pipeline_submission</code></li>
<li><code>fabricops_kit.activated_pipeline.shared.export_retained_submission</code></li>
<li><code>fabricops_kit.activated_pipeline.shared.manifest_digest</code></li>
<li><code>fabricops_kit.activated_pipeline.shared.metadata_path</code></li>
<li><code>fabricops_kit.activated_pipeline.shared.metadata_records</code></li>
<li><code>fabricops_kit.activated_pipeline.shared.mutate_metadata</code></li>
<li><code>fabricops_kit.activated_pipeline.shared.normalized_destination</code></li>
<li><code>fabricops_kit.activated_pipeline.shared.notebook_executable_digest</code></li>
<li><code>fabricops_kit.activated_pipeline.shared.persist_engineering_dry_run</code></li>
<li><code>fabricops_kit.activated_pipeline.shared.persist_engineering_submission</code></li>
<li><code>fabricops_kit.activated_pipeline.shared.promoted_notebook</code></li>
<li><code>fabricops_kit.activated_pipeline.shared.read_activation_history</code></li>
<li><code>fabricops_kit.activated_pipeline.shared.read_activations</code></li>
<li><code>fabricops_kit.activated_pipeline.shared.read_approvals</code></li>
<li><code>fabricops_kit.activated_pipeline.shared.read_registry</code></li>
<li><code>fabricops_kit.activated_pipeline.shared.replace_metadata_transaction</code></li>
<li><code>fabricops_kit.activated_pipeline.shared.resolve_activation_contract</code></li>
<li><code>fabricops_kit.activated_pipeline.shared.resolve_pipeline_identity</code></li>
<li><code>fabricops_kit.activated_pipeline.shared.resolve_promoted_operations</code></li>
<li><code>fabricops_kit.activated_pipeline.shared.restore_promoted_notebook</code></li>
<li><code>fabricops_kit.activated_pipeline.shared.review_submission_policy</code></li>
<li><code>fabricops_kit.activated_pipeline.shared.reviewed_contracts</code></li>
<li><code>fabricops_kit.activated_pipeline.shared.snapshot_file</code></li>
<li><code>fabricops_kit.activated_pipeline.shared.validate_activations</code></li>
<li><code>fabricops_kit.activated_pipeline.shared.validate_agreement</code></li>
<li><code>fabricops_kit.activated_pipeline.shared.validate_approvals</code></li>
<li><code>fabricops_kit.activated_pipeline.shared.validate_registry</code></li>
<li><code>fabricops_kit.activated_pipeline.shared.validate_submission</code></li>
<li><code>fabricops_kit.activated_pipeline.shared.verify_promotion_integrity</code></li>
<li><code>fabricops_kit.activated_pipeline.shared.verify_registry_approval</code></li>
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
<li><code>fabricops_kit.config.shared.build_table_id</code></li>
<li><code>fabricops_kit.config.shared.get_audit_timezone</code></li>
<li><code>fabricops_kit.config.shared.get_current_audit_timestamp</code></li>
<li><code>fabricops_kit.config.shared.get_default_fabric_context</code></li>
<li><code>fabricops_kit.config.shared.get_store</code></li>
<li><code>fabricops_kit.config.shared.normalize_audit_datetime</code></li>
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
<li><code>fabricops_kit.io.shared._validate_lakehouse_store</code></li>
<li><code>fabricops_kit.io.shared._validate_warehouse_store</code></li>
<li><code>fabricops_kit.io.shared.get_spark_session</code></li>
<li><code>fabricops_kit.io.shared.resolve_configured_lakehouse_table</code></li>
<li><code>fabricops_kit.io.shared.resolve_lakehouse_table_location</code></li>
<li><code>fabricops_kit.io.shared.resolve_store</code></li>
<li><code>fabricops_kit.io.shared.resolve_warehouse_name</code></li>
<li><code>fabricops_kit.io.shared.resolve_warehouse_table_location</code></li>
<li><code>fabricops_kit.io.shared.retry_delta_metadata</code></li>
<li><code>fabricops_kit.pipeline.finalize_pipeline._elapsed_seconds</code></li>
<li><code>fabricops_kit.pipeline.finalize_pipeline._format_duration</code></li>
<li><code>fabricops_kit.pipeline.finalize_pipeline._operation_summary_rows</code></li>
<li><code>fabricops_kit.pipeline.finalize_pipeline._print_pipeline_summary</code></li>
<li><code>fabricops_kit.pipeline.shared._contract_payload</code></li>
<li><code>fabricops_kit.pipeline.shared.canonical_pipeline_json</code></li>
<li><code>fabricops_kit.pipeline.shared.contract_guardrail_rows</code></li>
<li><code>fabricops_kit.pipeline.shared.current_pipeline_session</code></li>
<li><code>fabricops_kit.pipeline.shared.pipeline_physical_bindings</code></li>
<li><code>fabricops_kit.pipeline.shared.pipeline_record_content</code></li>
<li><code>fabricops_kit.pipeline.shared.resolve_physical_table_identity</code></li>
<li><code>fabricops_kit.pipeline.shared.validate_grain_parameters</code></li>
<li><code>fabricops_kit.pipeline.shared.validate_pipeline_id</code></li>
<li><code>fabricops_kit.pipeline.shared.validate_pipeline_profiling</code></li>
<li><code>fabricops_kit.pipeline.shared.validate_pipeline_run</code></li>
<li><code>fabricops_kit.pipeline.shared.validate_source_drift_configuration</code></li>
<li><code>fabricops_kit.pipeline.shared.validated_processing</code></li>
</ul>


</details>

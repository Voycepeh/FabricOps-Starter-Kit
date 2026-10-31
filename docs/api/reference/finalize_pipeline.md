# `finalize_pipeline`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-live reference-lifecycle-chip-prominent">Live</span>
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-live reference-lifecycle-chip-prominent">Live since 0.3.0</span>
</p>

> This function is part of the supported FabricOps public contract. Changes to its signature, behaviour, public export, or Live-critical dependencies require Live-contract review.

Complete execution and return Test results or commit the Live outcome.


## Usage notes

Call after all Reads, transformations and Writes, including read-only runs.


## Example usage

<div class="reference-example-usage" markdown="1">

```python
pipeline = setup_pipeline(pipeline_id="8f32a471-6c91-4b7e-9d13-2f0c947eab52", pipeline_mode="Ungoverned")
source = orchestrate_read(store="Bronze", schema="demo", table_name="orders")
pipeline_result = finalize_pipeline(pipeline)
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
A successful Write or cell never completes the whole pipeline by itself.
Open sessions require the current initialized notebook configuration and
runtime identity, whether passed explicitly or selected implicitly. Already
closed sessions retain their recorded outcome for repeat finalization.

Dry Run returns a session-only summary and persists no target, watermark,
processing state, profile observation or run metadata. Ungoverned and
Governed executions persist their real operational outcome. Governed
finalization also releases its activation reservation. Interrupted runs
remain incomplete and are never reported as successful finalization.

</div>

## See also

No related guides documented.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/pipeline/finalize_pipeline.py:159`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline/finalize_pipeline.py#L159-L223">View on GitHub</a>
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
| Live-critical dependencies | 66 |

### Release history

| Status | Version |
| --- | --- |
| Live | 0.3.0 |
| Live | 0.3.1 |

### Live-critical dependencies

<ul class="reference-compact-list">
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
<li><code>fabricops_kit.config.metadata_schemas.metadata_table_owner</code></li>
<li><code>fabricops_kit.config.metadata_schemas.metadata_table_physical_schema</code></li>
<li><code>fabricops_kit.config.metadata_schemas.metadata_table_schema_registry</code></li>
<li><code>fabricops_kit.config.metadata_schemas.validate_catalogue_value</code></li>
<li><code>fabricops_kit.config.shared._get_fabric_runtime_context</code></li>
<li><code>fabricops_kit.config.shared._get_fabric_runtime_metadata</code></li>
<li><code>fabricops_kit.config.shared._normalize_path_config</code></li>
<li><code>fabricops_kit.config.shared._validate_audit_timezone</code></li>
<li><code>fabricops_kit.config.shared.build_column_id</code></li>
<li><code>fabricops_kit.config.shared.get_audit_timezone</code></li>
<li><code>fabricops_kit.config.shared.get_current_audit_timestamp</code></li>
<li><code>fabricops_kit.config.shared.get_default_fabric_context</code></li>
<li><code>fabricops_kit.config.shared.get_store</code></li>
<li><code>fabricops_kit.config.shared.normalize_audit_datetime</code></li>
<li><code>fabricops_kit.config.shared.resolve_fabric_context</code></li>
<li><code>fabricops_kit.config.shared.resolve_runtime_context</code></li>
<li><code>fabricops_kit.config.shared.stable_metadata_id</code></li>
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
<li><code>fabricops_kit.pipeline.finalize_pipeline._elapsed_seconds</code></li>
<li><code>fabricops_kit.pipeline.finalize_pipeline._format_duration</code></li>
<li><code>fabricops_kit.pipeline.finalize_pipeline._operation_summary_rows</code></li>
<li><code>fabricops_kit.pipeline.finalize_pipeline._print_pipeline_summary</code></li>
<li><code>fabricops_kit.pipeline.shared._audit_literal_columns</code></li>
<li><code>fabricops_kit.pipeline.shared._canonical_profiled_dataframe</code></li>
<li><code>fabricops_kit.pipeline.shared._catalogue_dataframe_from_profiled</code></li>
<li><code>fabricops_kit.pipeline.shared._delete_profile_snapshot</code></li>
<li><code>fabricops_kit.pipeline.shared._frequency_metadata_dataframe</code></li>
<li><code>fabricops_kit.pipeline.shared._key_candidate_evidence</code></li>
<li><code>fabricops_kit.pipeline.shared._merge_pipeline_run_row</code></li>
<li><code>fabricops_kit.pipeline.shared._persist_grain_candidates</code></li>
<li><code>fabricops_kit.pipeline.shared._persist_profile_observation</code></li>
<li><code>fabricops_kit.pipeline.shared._profile_snapshot_id</code></li>
<li><code>fabricops_kit.pipeline.shared._read_pipeline_run_rows</code></li>
<li><code>fabricops_kit.pipeline.shared._replace_frequency_rows</code></li>
<li><code>fabricops_kit.pipeline.shared._replace_snapshot_rows</code></li>
<li><code>fabricops_kit.pipeline.shared._row_to_dict</code></li>
<li><code>fabricops_kit.pipeline.shared._stage_catalogue_profile_retry</code></li>
<li><code>fabricops_kit.pipeline.shared._upsert_catalogue_identities</code></li>
<li><code>fabricops_kit.pipeline.shared.canonical_pipeline_json</code></li>
<li><code>fabricops_kit.pipeline.shared.current_pipeline_session</code></li>
<li><code>fabricops_kit.pipeline.shared.persist_pipeline_run</code></li>
<li><code>fabricops_kit.pipeline.shared.pipeline_record_content</code></li>
<li><code>fabricops_kit.pipeline.shared.pipeline_run_row</code></li>
<li><code>fabricops_kit.pipeline.shared.publish_pipeline_testing_results</code></li>
<li><code>fabricops_kit.pipeline.shared.validate_pipeline_run</code></li>
</ul>


</details>

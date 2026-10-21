# `orchestrate_read`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-live reference-lifecycle-chip-prominent">Live</span>
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-live reference-lifecycle-chip-prominent">Live since 0.2.5</span>
</p>

> This function is part of the supported FabricOps public contract. Changes to its signature, behaviour, public export, or Live-critical dependencies require Live-contract review.

Run the observable standard governed source lifecycle.

<p class="reference-catalogue-item-meta reference-catalogue-item-badges">
<span class="reference-chip">02_pipeline</span>
</p>

## Usage notes

Use for the normal governed Read path before project PySpark transformation.


## Example usage

<div class="reference-example-usage" markdown="1">

```python
source = orchestrate_read(execution_plan=plan, store="Bronze", schema="demo", table_name="orders")
```

</div>

<details class="reference-signature-details" markdown="1">
<summary>Signature</summary>

## Signature

<div class="reference-api-definition" markdown="1">

```python
def orchestrate_read(
    *,
    execution_plan,
    store: str,
    schema: str | None,
    table_name: str,
    read_mode: str='full',
    query: str | None=None,
    read_parameters: dict[str, Any] | None=None,
    target_table_id: str | None=None,
    grain_discovery_enabled: bool=True,
    grain_discovery_max_columns: int=3,
    grain_discovery_max_candidates: int=8,
    frequency_enabled: bool=True,
    frequency_top_n: int | None=5,
    spark_session=None,
    verbose: bool=True,
    dq_diagnostics: str='sample',
) -> dict[str, Any]:
```

</div>

</details>

## Parameters

Required describes the Python signature. An optional parameter may still be needed for the selected mode or identity form; see its description. `—` means no signature default.

<div class="reference-input-table" markdown="1">

| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `execution_plan` | `PipelineExecutionPlan` | Yes | `—` | Required immutable plan from setup_pipeline in interactive or headless mode. Pass the same object to every Read and Write and execute the entire project then call finalize_pipeline(plan) for whole-run completion. Testing evaluates Freshness, Schema, Grain, Data Quality and Profile. With testing_writes=False, ordinary Catalogue/Profile/Source Observation commits are disabled; run records and Guardrail diagnostics still persist. Explicit real Testing writes permit normal metadata side effects to safe destinations. Live enforces one pinned approved revision. Environment names select routing. Empty or disabled optional Guardrails add no execution requirement. A configured check that cannot execute blocks Live and remains a Testing diagnostic. |
| `store` | `str` | Yes | `—` | Configured source store key. |
| `schema` | `str \| None` | Yes | `—` | Explicit physical schema; pass None for a schemaless store. |
| `table_name` | `str` | Yes | `—` | Physical source table name. |
| `read_mode` | `str` | No | `'full'` | Full reads profile the source; incremental reads retain checkpoint bounds. |
| `query` | `str \| None` | No | `None` | Read-only Warehouse query, supported for full reads only. |
| `read_parameters` | `dict[str, Any] \| None` | No | `None` | Incremental watermark_column; must agree with the selected contract. |
| `target_table_id` | `str \| None` | No | `None` | Required target for incremental reads, also a participant in the plan. |
| `grain_discovery_enabled` | `bool` | No | `True` | Discover candidate Grain keys during full-read profiling; contract Grain checks always run. |
| `grain_discovery_max_columns` | `int` | No | `3` | Positive maximum width of a candidate key. |
| `grain_discovery_max_candidates` | `int` | No | `8` | Positive maximum retained candidates at the smallest valid key width. |
| `frequency_enabled` | `bool` | No | `True` | Calculate optional frequency distributions during profiling. |
| `frequency_top_n` | `int \| None` | No | `5` | Maximum frequency values per column. |
| `spark_session` | `object` | No | `None` | Spark session shared by all stages. |
| `verbose` | `bool` | No | `True` | Print concise stage outcomes and summary. |
| `dq_diagnostics` | `str` | No | `'sample'` | Rule metrics plus bounded examples, no examples, or lazy full failures. |

</div>

## Returns

dict
    Source dataframe and identity, selected contract, execution_mode,
    applicable_guardrails, diagnostic results, profile, persistence_status,
    publication_status and checks_not_exercised. Testing retains blocking
    rule outcomes for inspection; Live stops on Block. Neither publishes data.

## Raises / Errors

ValueError
    For an invalid or inconsistent plan, mode, parameters or participant.
RuntimeError
    For a failed stage, retaining the original exception as its cause.

## See also

No related guides documented.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/pipeline/orchestrate_read.py:22`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline/orchestrate_read.py#L22-L155">View on GitHub</a>
</div>


<details class="reference-implementation-details" markdown="1">
<summary>Maintainer architecture details</summary>

## Contract impact

| Property | Value |
| --- | --- |
| Lifecycle | <span class="reference-chip reference-lifecycle-chip reference-lifecycle-live">Live</span> |
| Live since | 0.2.5 |
| Discontinued in | — |
| Contract classification | Live public function |
| Contract risk | Live |
| Live-critical dependencies | 180 |

### Release history

| Status | Version |
| --- | --- |
| Live | 0.2.5 |

### Live-critical dependencies

<ul class="reference-compact-list">
<li><code>fabricops_kit.activated_pipeline.shared.agreement_definition</code></li>
<li><code>fabricops_kit.activated_pipeline.shared.environment_activation</code></li>
<li><code>fabricops_kit.activated_pipeline.shared.exact_record</code></li>
<li><code>fabricops_kit.activated_pipeline.shared.manifest_digest</code></li>
<li><code>fabricops_kit.activated_pipeline.shared.metadata_records</code></li>
<li><code>fabricops_kit.activated_pipeline.shared.read_activation_state</code></li>
<li><code>fabricops_kit.activated_pipeline.shared.validate_agreement</code></li>
<li><code>fabricops_kit.activated_pipeline.shared.validate_manifest</code></li>
<li><code>fabricops_kit.activated_pipeline.shared.validate_testing_destinations</code></li>
<li><code>fabricops_kit.activated_pipeline.shared.verify_live_plan</code></li>
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
<li><code>fabricops_kit.config.shared.build_column_id</code></li>
<li><code>fabricops_kit.config.shared.build_table_id</code></li>
<li><code>fabricops_kit.config.shared.get_audit_timezone</code></li>
<li><code>fabricops_kit.config.shared.get_current_audit_timestamp</code></li>
<li><code>fabricops_kit.config.shared.get_default_fabric_context</code></li>
<li><code>fabricops_kit.config.shared.get_store</code></li>
<li><code>fabricops_kit.config.shared.is_table_not_found_error</code></li>
<li><code>fabricops_kit.config.shared.metadata_timestamp_sort_key</code></li>
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
<li><code>fabricops_kit.io.shared.resolve_warehouse_table_location</code></li>
<li><code>fabricops_kit.pipeline.check_dq.check_dq</code></li>
<li><code>fabricops_kit.pipeline.check_freshness.check_freshness</code></li>
<li><code>fabricops_kit.pipeline.check_grain.check_grain</code></li>
<li><code>fabricops_kit.pipeline.check_schema.check_schema</code></li>
<li><code>fabricops_kit.pipeline.pipeline_read._filter_lakehouse_incremental</code></li>
<li><code>fabricops_kit.pipeline.pipeline_read._resolve_requested_incremental_columns</code></li>
<li><code>fabricops_kit.pipeline.pipeline_read._warehouse_incremental_query</code></li>
<li><code>fabricops_kit.pipeline.pipeline_read._warehouse_watermark_literal</code></li>
<li><code>fabricops_kit.pipeline.profile_table._audit_literal_columns</code></li>
<li><code>fabricops_kit.pipeline.profile_table._automatic_frequency_columns</code></li>
<li><code>fabricops_kit.pipeline.profile_table._canonical_profiled_dataframe</code></li>
<li><code>fabricops_kit.pipeline.profile_table._catalogue_dataframe_from_profiled</code></li>
<li><code>fabricops_kit.pipeline.profile_table._delete_profile_snapshot</code></li>
<li><code>fabricops_kit.pipeline.profile_table._frequency_metadata_dataframe</code></li>
<li><code>fabricops_kit.pipeline.profile_table._key_candidate_evidence</code></li>
<li><code>fabricops_kit.pipeline.profile_table._key_candidate_payload</code></li>
<li><code>fabricops_kit.pipeline.profile_table._profile_snapshot_id</code></li>
<li><code>fabricops_kit.pipeline.profile_table._replace_frequency_rows</code></li>
<li><code>fabricops_kit.pipeline.profile_table._replace_snapshot_rows</code></li>
<li><code>fabricops_kit.pipeline.profile_table._scalar_frequency_columns</code></li>
<li><code>fabricops_kit.pipeline.profile_table._selected_frequency_columns</code></li>
<li><code>fabricops_kit.pipeline.profile_table._spark_profile_key_candidates</code></li>
<li><code>fabricops_kit.pipeline.profile_table._sql_identifier</code></li>
<li><code>fabricops_kit.pipeline.profile_table._sql_string</code></li>
<li><code>fabricops_kit.pipeline.profile_table._stage_catalogue_profile_retry</code></li>
<li><code>fabricops_kit.pipeline.profile_table._upsert_catalogue_identities</code></li>
<li><code>fabricops_kit.pipeline.profile_table._warehouse_columns</code></li>
<li><code>fabricops_kit.pipeline.profile_table._warehouse_frequency_query</code></li>
<li><code>fabricops_kit.pipeline.profile_table._warehouse_percentile_query</code></li>
<li><code>fabricops_kit.pipeline.profile_table._warehouse_profile_dataframes</code></li>
<li><code>fabricops_kit.pipeline.profile_table._warehouse_profile_key_candidates</code></li>
<li><code>fabricops_kit.pipeline.profile_table._warehouse_statistical_dataframe</code></li>
<li><code>fabricops_kit.pipeline.profile_table._warehouse_statistical_query</code></li>
<li><code>fabricops_kit.pipeline.profile_table._warehouse_type_name</code></li>
<li><code>fabricops_kit.pipeline.shared._actual_schema</code></li>
<li><code>fabricops_kit.pipeline.shared._apply_bypass_post_review_warning</code></li>
<li><code>fabricops_kit.pipeline.shared._candidate_hash</code></li>
<li><code>fabricops_kit.pipeline.shared._canonical_dq_rule_type</code></li>
<li><code>fabricops_kit.pipeline.shared._catalogue_value</code></li>
<li><code>fabricops_kit.pipeline.shared._coerce_date</code></li>
<li><code>fabricops_kit.pipeline.shared._coerce_datetime</code></li>
<li><code>fabricops_kit.pipeline.shared._compact_rows</code></li>
<li><code>fabricops_kit.pipeline.shared._compact_value</code></li>
<li><code>fabricops_kit.pipeline.shared._contract_payload</code></li>
<li><code>fabricops_kit.pipeline.shared._custom_expression_column</code></li>
<li><code>fabricops_kit.pipeline.shared._custom_expression_columns</code></li>
<li><code>fabricops_kit.pipeline.shared._custom_expression_tree</code></li>
<li><code>fabricops_kit.pipeline.shared._dq_applicable_expression</code></li>
<li><code>fabricops_kit.pipeline.shared._dq_checks_from_counts</code></li>
<li><code>fabricops_kit.pipeline.shared._dq_empty_failed_values</code></li>
<li><code>fabricops_kit.pipeline.shared._dq_failed_expression</code></li>
<li><code>fabricops_kit.pipeline.shared._dq_failed_value_schema</code></li>
<li><code>fabricops_kit.pipeline.shared._dq_failed_values_dataframe</code></li>
<li><code>fabricops_kit.pipeline.shared._dq_sample_failed_values</code></li>
<li><code>fabricops_kit.pipeline.shared._dq_sample_record</code></li>
<li><code>fabricops_kit.pipeline.shared._dq_tagged_dataframe</code></li>
<li><code>fabricops_kit.pipeline.shared._ensure_unambiguous_source_observation</code></li>
<li><code>fabricops_kit.pipeline.shared._evaluate_dq_rules</code></li>
<li><code>fabricops_kit.pipeline.shared._guardrail_schema_check_base</code></li>
<li><code>fabricops_kit.pipeline.shared._identifier</code></li>
<li><code>fabricops_kit.pipeline.shared._is_active_guardrail_rule</code></li>
<li><code>fabricops_kit.pipeline.shared._iso_date_value</code></li>
<li><code>fabricops_kit.pipeline.shared._latest_source_target_observation</code></li>
<li><code>fabricops_kit.pipeline.shared._load_active_dq_rules</code></li>
<li><code>fabricops_kit.pipeline.shared._max_column_value</code></li>
<li><code>fabricops_kit.pipeline.shared._merge_source_observation_records</code></li>
<li><code>fabricops_kit.pipeline.shared._normalize_datatype</code></li>
<li><code>fabricops_kit.pipeline.shared._normalize_dq_severity</code></li>
<li><code>fabricops_kit.pipeline.shared._observe_dataframe</code></li>
<li><code>fabricops_kit.pipeline.shared._observe_lakehouse</code></li>
<li><code>fabricops_kit.pipeline.shared._observe_partition_dataframe</code></li>
<li><code>fabricops_kit.pipeline.shared._orchestration_status</code></li>
<li><code>fabricops_kit.pipeline.shared._parse_parameters</code></li>
<li><code>fabricops_kit.pipeline.shared._parse_rule_parameters</code></li>
<li><code>fabricops_kit.pipeline.shared._physical_target_has_publication</code></li>
<li><code>fabricops_kit.pipeline.shared._portable_candidate_value</code></li>
<li><code>fabricops_kit.pipeline.shared._portable_contract_payload</code></li>
<li><code>fabricops_kit.pipeline.shared._profile_column_expr</code></li>
<li><code>fabricops_kit.pipeline.shared._profile_percent_expr</code></li>
<li><code>fabricops_kit.pipeline.shared._progress_key</code></li>
<li><code>fabricops_kit.pipeline.shared._publication_receipt</code></li>
<li><code>fabricops_kit.pipeline.shared._recover_completed_source_observations</code></li>
<li><code>fabricops_kit.pipeline.shared._row_to_dict</code></li>
<li><code>fabricops_kit.pipeline.shared._rule_review_status</code></li>
<li><code>fabricops_kit.pipeline.shared._run_orchestration_stage</code></li>
<li><code>fabricops_kit.pipeline.shared._select_rule</code></li>
<li><code>fabricops_kit.pipeline.shared._select_table_guardrail_rule</code></li>
<li><code>fabricops_kit.pipeline.shared._source_observation_signature</code></li>
<li><code>fabricops_kit.pipeline.shared._spark_sql_helpers</code></li>
<li><code>fabricops_kit.pipeline.shared._string_value</code></li>
<li><code>fabricops_kit.pipeline.shared._summarize_dq_guardrail</code></li>
<li><code>fabricops_kit.pipeline.shared._validate_dq_rules</code></li>
<li><code>fabricops_kit.pipeline.shared._validated_observation_identity</code></li>
<li><code>fabricops_kit.pipeline.shared._warehouse_observation_query</code></li>
<li><code>fabricops_kit.pipeline.shared._watermark_timestamp</code></li>
<li><code>fabricops_kit.pipeline.shared.build_frequency_distribution_dataframe</code></li>
<li><code>fabricops_kit.pipeline.shared.build_profile_dataframe</code></li>
<li><code>fabricops_kit.pipeline.shared.canonical_candidate_json</code></li>
<li><code>fabricops_kit.pipeline.shared.capture_source_observation</code></li>
<li><code>fabricops_kit.pipeline.shared.catalogue_authored_processing</code></li>
<li><code>fabricops_kit.pipeline.shared.check_dq_runtime</code></li>
<li><code>fabricops_kit.pipeline.shared.contract_guardrail_rows</code></li>
<li><code>fabricops_kit.pipeline.shared.display_table_identity</code></li>
<li><code>fabricops_kit.pipeline.shared.dq_tolerance_parameter</code></li>
<li><code>fabricops_kit.pipeline.shared.execution_result</code></li>
<li><code>fabricops_kit.pipeline.shared.freshness_check_core</code></li>
<li><code>fabricops_kit.pipeline.shared.get_current_freshness_evidence</code></li>
<li><code>fabricops_kit.pipeline.shared.grain_check_core</code></li>
<li><code>fabricops_kit.pipeline.shared.load_table_guardrail_rules</code></li>
<li><code>fabricops_kit.pipeline.shared.observation_rows</code></li>
<li><code>fabricops_kit.pipeline.shared.persistence_permitted</code></li>
<li><code>fabricops_kit.pipeline.shared.pipeline_candidate</code></li>
<li><code>fabricops_kit.pipeline.shared.pipeline_guardrail_types</code></li>
<li><code>fabricops_kit.pipeline.shared.pipeline_physical_bindings</code></li>
<li><code>fabricops_kit.pipeline.shared.prepare_pipeline_execution</code></li>
<li><code>fabricops_kit.pipeline.shared.print_guardrail_result</code></li>
<li><code>fabricops_kit.pipeline.shared.print_pipeline_contract</code></li>
<li><code>fabricops_kit.pipeline.shared.resolve_catalogue_table_identity</code></li>
<li><code>fabricops_kit.pipeline.shared.resolve_freshness_observation_column</code></li>
<li><code>fabricops_kit.pipeline.shared.resolve_incremental_observation_columns</code></li>
<li><code>fabricops_kit.pipeline.shared.resolve_incremental_source_scope</code></li>
<li><code>fabricops_kit.pipeline.shared.resolve_physical_table_identity</code></li>
<li><code>fabricops_kit.pipeline.shared.resolve_pipeline_data_contract</code></li>
<li><code>fabricops_kit.pipeline.shared.resolve_profiled_columns</code></li>
<li><code>fabricops_kit.pipeline.shared.resolve_source_drift_observation_columns</code></li>
<li><code>fabricops_kit.pipeline.shared.schema_check_core</code></li>
<li><code>fabricops_kit.pipeline.shared.select_table_guardrail_rule</code></li>
<li><code>fabricops_kit.pipeline.shared.set_current_source_observation</code></li>
<li><code>fabricops_kit.pipeline.shared.source_observation_run_id</code></li>
<li><code>fabricops_kit.pipeline.shared.validate_grain_parameters</code></li>
<li><code>fabricops_kit.pipeline.shared.write_guardrail_result_row</code></li>
</ul>


</details>

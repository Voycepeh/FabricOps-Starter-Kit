# `orchestrate_write`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-live reference-lifecycle-chip-prominent">Live</span>
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-live reference-lifecycle-chip-prominent">Live since 0.2.5</span>
</p>

> This function is part of the supported FabricOps public contract. Changes to its signature, behaviour, public export, or Live-critical dependencies require Live-contract review.

Run the observable standard governed target lifecycle.

<p class="reference-catalogue-item-meta reference-catalogue-item-badges">
<span class="reference-chip">02_pipeline</span>
</p>

## Usage notes

Use for the normal governed publication path after project PySpark transformation.


## Example usage

<div class="reference-example-usage" markdown="1">

```python
result = orchestrate_write(transformed_df, execution_plan=plan, sources=[source], store="Silver", schema="demo", table_name="orders", write_mode="overwrite")
```

</div>


<details class="reference-signature-details" markdown="1">
<summary>Signature</summary>

## Signature

<div class="reference-api-definition" markdown="1">

```python
def orchestrate_write(
    dataframe: Any,
    *,
    execution_plan,
    sources: Iterable[dict[str, Any]],
    store: str,
    schema: str | None,
    table_name: str,
    write_mode: str,
    write_parameters: dict[str, Any] | None=None,
    repartition_by: int | None=None,
    grain_discovery_enabled: bool=True,
    grain_discovery_max_columns: int=3,
    grain_discovery_max_candidates: int=8,
    frequency_enabled: bool=True,
    frequency_top_n: int | None=5,
    existing_mapping=None,
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
| `dataframe` | `Any` | Yes | `—` | Transformed Spark DataFrame; Sensitive Data treatment prepares the input. |
| `execution_plan` | `PipelineExecutionPlan` | Yes | `—` | Same required plan as all participating Reads. Execute all reads, transformations and writes inside with plan: for automatic whole-run completion. Testing evaluates processing, guardrails and incremental safety. Explicit testing_writes=True permits real publication to declared safe destinations, with mappings, checkpoints and normal metadata side effects. Otherwise Testing evaluates without publication. Live enforces the pinned approved contracts and ownership and stops on Block before publication. |
| `sources` | `Iterable[dict[str, Any]]` | Yes | `—` | Read results from this exact plan for the sources actually feeding this target. |
| `store` | `str` | Yes | `—` | Configured target store key. |
| `schema` | `str \| None` | Yes | `—` | Explicit physical schema; pass None for a schemaless store. |
| `table_name` | `str` | Yes | `—` | Physical target table name. |
| `write_mode` | `str` | Yes | `—` | Proposed strategy; must match the selected contract processing definition. |
| `write_parameters` | `dict[str, Any] \| None` | No | `None` | Strategy parameters including SCD key_columns and SCD2 effective_column. |
| `repartition_by` | `int \| None` | No | `None` | Physical write partition count for Live. |
| `grain_discovery_enabled` | `bool` | No | `True` | Discover candidate Grain keys during persisted-target profiling; governed checks always run. |
| `grain_discovery_max_columns` | `int` | No | `3` | Positive maximum width of a candidate key. |
| `grain_discovery_max_candidates` | `int` | No | `8` | Positive maximum retained candidates at the smallest valid key width. |
| `frequency_enabled` | `bool` | No | `True` | Calculate optional frequency distributions during profiling. |
| `frequency_top_n` | `int \| None` | No | `5` | Maximum frequency rows per column. |
| `existing_mapping` | `object` | No | `None` | Caller-managed Sensitive Data mapping; incompatible with a configured vault. Existing assignments are reused. The returned sensitive_result.support_mapping remains caller-owned; persist it only in explicitly authorized write workflows, then unpersist() its cache after consumption. A configured restricted mapping store is read-only during evaluation-only Testing and reused/updated during authorized writes. Failures release the cache. |
| `spark_session` | `object` | No | `None` | Spark session used throughout. |
| `verbose` | `bool` | No | `True` | Print concise stages and outcome. |
| `dq_diagnostics` | `str` | No | `'sample'` | Exact metrics with bounded samples, no samples or lazy full violations. |

</div>

## Advanced examples

<div class="reference-example-usage" markdown="1">

```python
result = orchestrate_write(transformed_df, execution_plan=plan, sources=[source],
    store="Silver", schema="demo", table_name="orders", write_mode="overwrite")
```

</div>

## Returns

dict
    Prepared dataframe, selected contract, execution_mode, Guardrail outcomes,
    schema_result, sensitive_result, source_drift_results, grain_result,
    dq_result, source_guardrail_results, write_metrics, published, persistence_status and explicit dry-run
    limits. Testing failures remain diagnostic results, never publication success.
    source_guardrail_results lists the configured Read rules required by the
    contributing sources; disabled and unconfigured checks impose no requirement.
    Live returns the actual publication outcome. Metadata commits across Fabric
    stores are separate lifecycle operations, not one atomic transaction.

## Raises / Errors

ValueError
    For inconsistent participants, plans, processing or parameter definitions.
RuntimeError
    For a failed Live stage. A Profile failure after publication retains
    published=True and write_metrics on the exception; retry recovery is unchanged.

## See also

No related guides documented.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/pipeline/orchestrate_write.py:26`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline/orchestrate_write.py#L26-L239">View on GitHub</a>
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
| Live-critical dependencies | 205 |

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
<li><code>fabricops_kit.data_contract.scheduled_refresh._fabric_schedules_json</code></li>
<li><code>fabricops_kit.data_contract.scheduled_refresh._time_value</code></li>
<li><code>fabricops_kit.data_contract.scheduled_refresh.canonical_scheduled_refresh</code></li>
<li><code>fabricops_kit.data_contract.scheduled_refresh.discover_scheduled_refresh</code></li>
<li><code>fabricops_kit.data_contract.scheduled_refresh.normalize_scheduled_refresh</code></li>
<li><code>fabricops_kit.data_contract.shared.validate_sensitive_data_parameters</code></li>
<li><code>fabricops_kit.io.shared._build_warehouse_object_name</code></li>
<li><code>fabricops_kit.io.shared._drop_warehouse_stage_best_effort</code></li>
<li><code>fabricops_kit.io.shared._join_lakehouse_area_path</code></li>
<li><code>fabricops_kit.io.shared._normalize_schema_name</code></li>
<li><code>fabricops_kit.io.shared._normalize_table_name</code></li>
<li><code>fabricops_kit.io.shared._quoted_warehouse_identifier</code></li>
<li><code>fabricops_kit.io.shared._require_fabric_connector</code></li>
<li><code>fabricops_kit.io.shared._resolve_lakehouse_schema</code></li>
<li><code>fabricops_kit.io.shared._resolve_lakehouse_table_path</code></li>
<li><code>fabricops_kit.io.shared._validate_lakehouse_store</code></li>
<li><code>fabricops_kit.io.shared._validate_warehouse_store</code></li>
<li><code>fabricops_kit.io.shared._warehouse_column_list</code></li>
<li><code>fabricops_kit.io.shared._warehouse_null_safe_difference</code></li>
<li><code>fabricops_kit.io.shared.execute_warehouse_processing</code></li>
<li><code>fabricops_kit.io.shared.execute_warehouse_sql</code></li>
<li><code>fabricops_kit.io.shared.get_spark_session</code></li>
<li><code>fabricops_kit.io.shared.read_warehouse_synapsesql</code></li>
<li><code>fabricops_kit.io.shared.repartition_dataframe_for_write</code></li>
<li><code>fabricops_kit.io.shared.resolve_configured_lakehouse_table</code></li>
<li><code>fabricops_kit.io.shared.resolve_configured_warehouse_table</code></li>
<li><code>fabricops_kit.io.shared.resolve_lakehouse_table_location</code></li>
<li><code>fabricops_kit.io.shared.resolve_store</code></li>
<li><code>fabricops_kit.io.shared.resolve_warehouse_table_location</code></li>
<li><code>fabricops_kit.io.shared.write_warehouse_synapsesql</code></li>
<li><code>fabricops_kit.pipeline.check_dq.check_dq</code></li>
<li><code>fabricops_kit.pipeline.check_grain.check_grain</code></li>
<li><code>fabricops_kit.pipeline.check_schema.check_schema</code></li>
<li><code>fabricops_kit.pipeline.check_sensitive_data.check_sensitive_data</code></li>
<li><code>fabricops_kit.pipeline.check_source_drift.check_source_drift</code></li>
<li><code>fabricops_kit.pipeline.pipeline_write._persist_target_processing</code></li>
<li><code>fabricops_kit.pipeline.pipeline_write._physical_processing_definition</code></li>
<li><code>fabricops_kit.pipeline.pipeline_write._source_table_ids</code></li>
<li><code>fabricops_kit.pipeline.pipeline_write._target_has_rows</code></li>
<li><code>fabricops_kit.pipeline.pipeline_write._validate_target_writer_ownership</code></li>
<li><code>fabricops_kit.pipeline.pipeline_write._warehouse_target_exists</code></li>
<li><code>fabricops_kit.pipeline.pipeline_write._write_scope</code></li>
<li><code>fabricops_kit.pipeline.pipeline_write._writer_scheduled_refresh</code></li>
<li><code>fabricops_kit.pipeline.pipeline_write.pipeline_write</code></li>
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
<li><code>fabricops_kit.pipeline.shared._apply_token_mapping</code></li>
<li><code>fabricops_kit.pipeline.shared._bucket_column</code></li>
<li><code>fabricops_kit.pipeline.shared._build_token_mapping</code></li>
<li><code>fabricops_kit.pipeline.shared._candidate_hash</code></li>
<li><code>fabricops_kit.pipeline.shared._canonical_dq_rule_type</code></li>
<li><code>fabricops_kit.pipeline.shared._catalogue_value</code></li>
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
<li><code>fabricops_kit.pipeline.shared._evaluate_dq_rules</code></li>
<li><code>fabricops_kit.pipeline.shared._guardrail_schema_check_base</code></li>
<li><code>fabricops_kit.pipeline.shared._is_active_guardrail_rule</code></li>
<li><code>fabricops_kit.pipeline.shared._load_active_dq_rules</code></li>
<li><code>fabricops_kit.pipeline.shared._mask_column</code></li>
<li><code>fabricops_kit.pipeline.shared._merge_source_observation_records</code></li>
<li><code>fabricops_kit.pipeline.shared._normalize_datatype</code></li>
<li><code>fabricops_kit.pipeline.shared._normalize_dq_severity</code></li>
<li><code>fabricops_kit.pipeline.shared._orchestration_status</code></li>
<li><code>fabricops_kit.pipeline.shared._parameters</code></li>
<li><code>fabricops_kit.pipeline.shared._parse_parameters</code></li>
<li><code>fabricops_kit.pipeline.shared._parse_rule_parameters</code></li>
<li><code>fabricops_kit.pipeline.shared._portable_candidate_value</code></li>
<li><code>fabricops_kit.pipeline.shared._portable_contract_payload</code></li>
<li><code>fabricops_kit.pipeline.shared._previous_source_target_observation</code></li>
<li><code>fabricops_kit.pipeline.shared._profile_column_expr</code></li>
<li><code>fabricops_kit.pipeline.shared._profile_percent_expr</code></li>
<li><code>fabricops_kit.pipeline.shared._row_to_dict</code></li>
<li><code>fabricops_kit.pipeline.shared._rule_review_status</code></li>
<li><code>fabricops_kit.pipeline.shared._run_orchestration_stage</code></li>
<li><code>fabricops_kit.pipeline.shared._select_rule</code></li>
<li><code>fabricops_kit.pipeline.shared._select_table_guardrail_rule</code></li>
<li><code>fabricops_kit.pipeline.shared._spark_sql_helpers</code></li>
<li><code>fabricops_kit.pipeline.shared._string_value</code></li>
<li><code>fabricops_kit.pipeline.shared._summarize_dq_guardrail</code></li>
<li><code>fabricops_kit.pipeline.shared._validate_dq_rules</code></li>
<li><code>fabricops_kit.pipeline.shared._validate_token_mapping</code></li>
<li><code>fabricops_kit.pipeline.shared._warehouse_publication_record</code></li>
<li><code>fabricops_kit.pipeline.shared.add_target_audit_fields</code></li>
<li><code>fabricops_kit.pipeline.shared.build_frequency_distribution_dataframe</code></li>
<li><code>fabricops_kit.pipeline.shared.build_profile_dataframe</code></li>
<li><code>fabricops_kit.pipeline.shared.canonical_candidate_json</code></li>
<li><code>fabricops_kit.pipeline.shared.catalogue_authored_processing</code></li>
<li><code>fabricops_kit.pipeline.shared.check_dq_runtime</code></li>
<li><code>fabricops_kit.pipeline.shared.check_sensitive_data_rules</code></li>
<li><code>fabricops_kit.pipeline.shared.check_source_drift_for_target</code></li>
<li><code>fabricops_kit.pipeline.shared.commit_pipeline_write_success</code></li>
<li><code>fabricops_kit.pipeline.shared.contract_guardrail_rows</code></li>
<li><code>fabricops_kit.pipeline.shared.deployed_notebook_fingerprint</code></li>
<li><code>fabricops_kit.pipeline.shared.display_table_identity</code></li>
<li><code>fabricops_kit.pipeline.shared.dq_tolerance_parameter</code></li>
<li><code>fabricops_kit.pipeline.shared.evaluate_source_drift_guardrail</code></li>
<li><code>fabricops_kit.pipeline.shared.execute_lakehouse_processing</code></li>
<li><code>fabricops_kit.pipeline.shared.execution_result</code></li>
<li><code>fabricops_kit.pipeline.shared.get_current_source_observation</code></li>
<li><code>fabricops_kit.pipeline.shared.grain_check_core</code></li>
<li><code>fabricops_kit.pipeline.shared.incremental_publication_scopes</code></li>
<li><code>fabricops_kit.pipeline.shared.lineage_id</code></li>
<li><code>fabricops_kit.pipeline.shared.load_table_guardrail_rules</code></li>
<li><code>fabricops_kit.pipeline.shared.notebook_executable_fingerprint</code></li>
<li><code>fabricops_kit.pipeline.shared.observation_rows</code></li>
<li><code>fabricops_kit.pipeline.shared.persist_lineage_participation</code></li>
<li><code>fabricops_kit.pipeline.shared.persistence_permitted</code></li>
<li><code>fabricops_kit.pipeline.shared.pipeline_candidate</code></li>
<li><code>fabricops_kit.pipeline.shared.pipeline_guardrail_types</code></li>
<li><code>fabricops_kit.pipeline.shared.pipeline_physical_bindings</code></li>
<li><code>fabricops_kit.pipeline.shared.prepare_pipeline_execution</code></li>
<li><code>fabricops_kit.pipeline.shared.print_guardrail_result</code></li>
<li><code>fabricops_kit.pipeline.shared.print_pipeline_contract</code></li>
<li><code>fabricops_kit.pipeline.shared.resolve_catalogue_table_identity</code></li>
<li><code>fabricops_kit.pipeline.shared.resolve_physical_table_identity</code></li>
<li><code>fabricops_kit.pipeline.shared.resolve_pipeline_data_contract</code></li>
<li><code>fabricops_kit.pipeline.shared.resolve_profiled_columns</code></li>
<li><code>fabricops_kit.pipeline.shared.resolve_scd1_business_columns</code></li>
<li><code>fabricops_kit.pipeline.shared.resolve_scd2_tracked_columns</code></li>
<li><code>fabricops_kit.pipeline.shared.resolve_table_processing_definition</code></li>
<li><code>fabricops_kit.pipeline.shared.resolve_target_audit_fields</code></li>
<li><code>fabricops_kit.pipeline.shared.schema_check_core</code></li>
<li><code>fabricops_kit.pipeline.shared.select_table_guardrail_rule</code></li>
<li><code>fabricops_kit.pipeline.shared.snapshot_pipeline_write_observations</code></li>
<li><code>fabricops_kit.pipeline.shared.source_guardrail_results</code></li>
<li><code>fabricops_kit.pipeline.shared.source_observation_run_id</code></li>
<li><code>fabricops_kit.pipeline.shared.stage_pipeline_write_observations</code></li>
<li><code>fabricops_kit.pipeline.shared.tested_contract_identities</code></li>
<li><code>fabricops_kit.pipeline.shared.validate_grain_parameters</code></li>
<li><code>fabricops_kit.pipeline.shared.validate_processing_input</code></li>
<li><code>fabricops_kit.pipeline.shared.validated_processing</code></li>
<li><code>fabricops_kit.pipeline.shared.write_guardrail_result_row</code></li>
</ul>


</details>

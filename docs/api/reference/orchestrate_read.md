# `orchestrate_read`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-live reference-lifecycle-chip-prominent">Live</span>
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-live reference-lifecycle-chip-prominent">Live since 0.2.5</span>
</p>

> This function is part of the supported FabricOps public contract. Changes to its signature, behaviour, public export, or Live-critical dependencies require Live-contract review.

Run the observable standard governed source lifecycle.

<p class="reference-catalogue-item-meta reference-catalogue-item-badges">
<span class="reference-chip">02_pipeline</span>
<span class="reference-chip">02A_full_refresh_demo</span>
<span class="reference-chip">02B_incremental_append_demo</span>
<span class="reference-chip">02C_scd_demo</span>
</p>

## Usage notes

Use for the normal governed Read path before project PySpark transformation.


## Example usage

<div class="reference-example-usage" markdown="1">

```python
source = orchestrate_read(store="Bronze", schema="demo", table_name="orders")
```

</div>


<details class="reference-signature-details" markdown="1">
<summary>Signature</summary>

## Signature

<div class="reference-api-definition" markdown="1">

```python
def orchestrate_read(
    *,
    store: str,
    schema: str | None=None,
    table_name: str | None=None,
    read_mode: str='full',
    query: str | None=None,
    read_parameters: dict[str, Any] | None=None,
    target_store: str | None=None,
    target_schema: str | None=None,
    target_table_name: str | None=None,
    verbose: bool=False,
    dq_diagnostics: str='sample',
    relative_path: str | None=None,
    file_format: str | None=None,
    read_options: dict[str, Any] | None=None,
) -> dict[str, Any]:
```

</div>

</details>

## Parameters

Required describes the Python signature. An optional parameter may still be needed for the selected mode or identity form; see its description. `—` means no signature default.

<div class="reference-input-table" markdown="1">

| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `store` | `str` | Yes | `—` | Configured source store key. |
| `schema` | `str \| None` | No | `None` | Explicit physical schema; pass None for a schemaless store. |
| `table_name` | `str \| None` | No | `None` | Physical source table name. |
| `read_mode` | `str` | No | `'full'` | Full reads profile the source; incremental reads retain checkpoint bounds. |
| `query` | `str \| None` | No | `None` | Read-only Spark SQL on a Lakehouse or T-SQL on a Warehouse, for full reads only. Lakehouse SQL binds the declared source through configured OneLake routing. Simple integer TOP projections can convert to LIMIT; complex T-SQL requires native Spark SQL and otherwise raises ValueError. |
| `read_parameters` | `dict[str, Any] \| None` | No | `None` | Required for incremental reads; Engineering watermark_column captured by Pipeline Activation. |
| `target_store` | `str \| None` | No | `None` | Configured target store key; required for incremental reads. |
| `target_schema` | `str \| None` | No | `None` | Physical target schema; omit for a schemaless store or configured default. |
| `target_table_name` | `str \| None` | No | `None` | Physical target table name; required for incremental reads. The resolved target must be an authorized target participant in the active plan. Source and target stores may route to different workspaces. |
| `verbose` | `bool` | No | `False` | Print concise stage outcomes and summary. |
| `dq_diagnostics` | `str` | No | `'sample'` | Rule metrics plus bounded examples, no examples, or lazy full failures. |
| `relative_path` | `str \| None` | No | `None` | File, folder or wildcard selector beneath the configured Lakehouse Files root. Brace expansion is unsupported because alternatives can escape that root. Mutually exclusive with table_name, schema, query and target coordinates. |
| `file_format` | `str \| None` | No | `None` | Required for file reads. Uses the corresponding foundational reader. |
| `read_options` | `dict[str, Any] \| None` | No | `None` | Format-specific reader keyword settings, retained exactly for approval. Options cannot override the source location or execution context. |

</div>

## Advanced examples

<div class="reference-example-usage" markdown="1">

```python
orders = orchestrate_read(store="Bronze", schema="demo", table_name="orders")
changes = orchestrate_read(
    store="Bronze", schema="demo", table_name="orders", read_mode="incremental",
    target_store="Silver", target_schema="demo", target_table_name="orders_clean",
)
```

</div>

## Returns

dict
    Governed source dataframe, execution identity, Guardrail outcomes, read_metrics, profile_result and orchestration_stages.
    ``read_metrics.rows_read`` and the notebook summary describe the exact
    returned scope. For incremental reads this is the target-specific batch,
    never the complete physical Source Observation count.

Raises RuntimeError when no pipeline is active or a persistent stage fails, and
ValueError for an invalid operation or inconsistent approved configuration.

## Raises / Errors

Not documented yet

## Behavior and scope

<div class="reference-docstring-intro" markdown="1">

Define store, schema, table_name and any full/incremental/query options.
Alternatively select a Lakehouse file, folder or wildcard using relative_path,
file_format and read_options. Files support full reads only and retain their
stable Source ID, with no Table ID. Foundational readers remain independent.
File profiles are calculated in memory per execution (including persistent
modes), using the pipeline row limit; no table profile snapshot is persisted.
A replaced file can be read again in a new execution; no exactly-once or
immutable-file guarantee is provided.
Spark, execution authority and reporting come from setup_pipeline. The result
retains its dataframe, canonical Table ID or file Source ID and Guardrail diagnostics. Reads
register pipeline-level participation for subsequent Writes; this is not
exact DataFrame lineage. Governed blocks failed contract checks; Dry Run never commits.
FabricOps resolves source and target Table IDs through configured workspace routing.
dq_diagnostics accepts sample, none or full for explicit debugging.

Table profiling uses pipeline-owned settings and shared
persisted completion history. Full table reads reuse the exact returned DataFrame;
query and incremental Reads profile the physical source when due, bounded only
by setup_pipeline(profiling_max_rows=...).
A restricted query never replaces full-source observations or profile snapshots.
Disabled or not-due activities cause no separate profiling scan; configured
Source Observation, Freshness and Source Drift checks retain their physical scope. Successful
Dry Run retains calculated observations only in the session without consuming
persisted schedules. Guardrail
checks run regardless of profiling eligibility.

When statistical profiling completes, the operation summary is followed by a
readable profile table even with ``verbose=False``. Native Fabric display has
a text fallback; the preview shows at most 100 columns and 120 characters per
text cell. Complete-table, bounded-selection and Dry Run scopes are labelled.
Skipped or not-due profiling shows no historical results. Presentation reuses
current aggregates and cannot fail a successful operation. ``verbose=True``
adds operational diagnostics. Returned profiling structures are unchanged.

</div>

## See also

No related guides documented.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/pipeline/orchestrate_read.py:28`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline/orchestrate_read.py#L28-L233">View on GitHub</a>
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
| Live-critical dependencies | 264 |

### Release history

| Status | Version |
| --- | --- |
| Live | 0.2.5 |
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
<li><code>fabricops_kit.activated_pipeline.shared.exact_record</code></li>
<li><code>fabricops_kit.activated_pipeline.shared.manifest_digest</code></li>
<li><code>fabricops_kit.activated_pipeline.shared.metadata_records</code></li>
<li><code>fabricops_kit.activated_pipeline.shared.normalized_destination</code></li>
<li><code>fabricops_kit.activated_pipeline.shared.notebook_executable_digest</code></li>
<li><code>fabricops_kit.activated_pipeline.shared.promoted_notebook</code></li>
<li><code>fabricops_kit.activated_pipeline.shared.read_approvals</code></li>
<li><code>fabricops_kit.activated_pipeline.shared.read_registry</code></li>
<li><code>fabricops_kit.activated_pipeline.shared.resolve_activation_contract</code></li>
<li><code>fabricops_kit.activated_pipeline.shared.resolve_promoted_operations</code></li>
<li><code>fabricops_kit.activated_pipeline.shared.snapshot_file</code></li>
<li><code>fabricops_kit.activated_pipeline.shared.validate_agreement</code></li>
<li><code>fabricops_kit.activated_pipeline.shared.validate_approvals</code></li>
<li><code>fabricops_kit.activated_pipeline.shared.validate_file_execution_authorizations</code></li>
<li><code>fabricops_kit.activated_pipeline.shared.validate_registry</code></li>
<li><code>fabricops_kit.activated_pipeline.shared.validate_submission</code></li>
<li><code>fabricops_kit.activated_pipeline.shared.verify_governed_plan</code></li>
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
<li><code>fabricops_kit.config.metadata_schemas.decode_metadata_dataframe</code></li>
<li><code>fabricops_kit.config.metadata_schemas.decode_metadata_row</code></li>
<li><code>fabricops_kit.config.metadata_schemas.encode_metadata_row</code></li>
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
<li><code>fabricops_kit.data_contract.shared.file_source_identity</code></li>
<li><code>fabricops_kit.data_contract.shared.normalize_guardrail_action</code></li>
<li><code>fabricops_kit.data_contract.shared.validate_contract_definitions</code></li>
<li><code>fabricops_kit.data_contract.shared.validate_contract_source</code></li>
<li><code>fabricops_kit.data_contract.shared.validate_grain_contract</code></li>
<li><code>fabricops_kit.data_contract.shared.validate_sensitive_data_parameters</code></li>
<li><code>fabricops_kit.io.shared._build_warehouse_object_name</code></li>
<li><code>fabricops_kit.io.shared._join_lakehouse_area_path</code></li>
<li><code>fabricops_kit.io.shared._normalize_schema_name</code></li>
<li><code>fabricops_kit.io.shared._normalize_table_name</code></li>
<li><code>fabricops_kit.io.shared._resolve_lakehouse_schema</code></li>
<li><code>fabricops_kit.io.shared._resolve_lakehouse_table_path</code></li>
<li><code>fabricops_kit.io.shared._validate_lakehouse_store</code></li>
<li><code>fabricops_kit.io.shared._validate_relative_path</code></li>
<li><code>fabricops_kit.io.shared._validate_warehouse_store</code></li>
<li><code>fabricops_kit.io.shared.get_spark_session</code></li>
<li><code>fabricops_kit.io.shared.resolve_configured_file_path</code></li>
<li><code>fabricops_kit.io.shared.resolve_configured_lakehouse_table</code></li>
<li><code>fabricops_kit.io.shared.resolve_lakehouse_file_location</code></li>
<li><code>fabricops_kit.io.shared.resolve_lakehouse_file_path</code></li>
<li><code>fabricops_kit.io.shared.resolve_lakehouse_table_location</code></li>
<li><code>fabricops_kit.io.shared.resolve_store</code></li>
<li><code>fabricops_kit.io.shared.resolve_warehouse_name</code></li>
<li><code>fabricops_kit.io.shared.resolve_warehouse_table_location</code></li>
<li><code>fabricops_kit.io.shared.retry_delta_metadata</code></li>
<li><code>fabricops_kit.io.shared.validate_select_query</code></li>
<li><code>fabricops_kit.pipeline.check_dq.check_dq</code></li>
<li><code>fabricops_kit.pipeline.check_freshness.check_freshness</code></li>
<li><code>fabricops_kit.pipeline.check_schema.check_schema</code></li>
<li><code>fabricops_kit.pipeline.pipeline_read._filter_lakehouse_incremental</code></li>
<li><code>fabricops_kit.pipeline.pipeline_read._lakehouse_query</code></li>
<li><code>fabricops_kit.pipeline.pipeline_read._measure_returned_rows</code></li>
<li><code>fabricops_kit.pipeline.pipeline_read._resolve_requested_incremental_columns</code></li>
<li><code>fabricops_kit.pipeline.pipeline_read._warehouse_incremental_query</code></li>
<li><code>fabricops_kit.pipeline.pipeline_read._warehouse_watermark_literal</code></li>
<li><code>fabricops_kit.pipeline.pipeline_read.pipeline_read</code></li>
<li><code>fabricops_kit.pipeline.resolve_table_id.resolve_table_id</code></li>
<li><code>fabricops_kit.pipeline.shared._actual_schema</code></li>
<li><code>fabricops_kit.pipeline.shared._apply_bypass_post_review_warning</code></li>
<li><code>fabricops_kit.pipeline.shared._audit_literal_columns</code></li>
<li><code>fabricops_kit.pipeline.shared._automatic_frequency_columns</code></li>
<li><code>fabricops_kit.pipeline.shared._canonical_dq_rule_type</code></li>
<li><code>fabricops_kit.pipeline.shared._canonical_profiled_dataframe</code></li>
<li><code>fabricops_kit.pipeline.shared._catalogue_dataframe_from_profiled</code></li>
<li><code>fabricops_kit.pipeline.shared._catalogue_value</code></li>
<li><code>fabricops_kit.pipeline.shared._coerce_date</code></li>
<li><code>fabricops_kit.pipeline.shared._coerce_datetime</code></li>
<li><code>fabricops_kit.pipeline.shared._compact_rows</code></li>
<li><code>fabricops_kit.pipeline.shared._compact_value</code></li>
<li><code>fabricops_kit.pipeline.shared._contract_payload</code></li>
<li><code>fabricops_kit.pipeline.shared._custom_expression_column</code></li>
<li><code>fabricops_kit.pipeline.shared._custom_expression_columns</code></li>
<li><code>fabricops_kit.pipeline.shared._custom_expression_tree</code></li>
<li><code>fabricops_kit.pipeline.shared._delete_profile_snapshot</code></li>
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
<li><code>fabricops_kit.pipeline.shared._format_value</code></li>
<li><code>fabricops_kit.pipeline.shared._frequency_metadata_dataframe</code></li>
<li><code>fabricops_kit.pipeline.shared._freshness_timestamp</code></li>
<li><code>fabricops_kit.pipeline.shared._guardrail_schema_check_base</code></li>
<li><code>fabricops_kit.pipeline.shared._identifier</code></li>
<li><code>fabricops_kit.pipeline.shared._is_active_guardrail_rule</code></li>
<li><code>fabricops_kit.pipeline.shared._iso_date_value</code></li>
<li><code>fabricops_kit.pipeline.shared._key_candidate_evidence</code></li>
<li><code>fabricops_kit.pipeline.shared._key_candidate_payload</code></li>
<li><code>fabricops_kit.pipeline.shared._latest_source_target_observation</code></li>
<li><code>fabricops_kit.pipeline.shared._load_active_dq_rules</code></li>
<li><code>fabricops_kit.pipeline.shared._max_column_value</code></li>
<li><code>fabricops_kit.pipeline.shared._merge_pipeline_run_row</code></li>
<li><code>fabricops_kit.pipeline.shared._merge_source_observation_records</code></li>
<li><code>fabricops_kit.pipeline.shared._metadata_hash</code></li>
<li><code>fabricops_kit.pipeline.shared._normalize_datatype</code></li>
<li><code>fabricops_kit.pipeline.shared._normalize_dq_severity</code></li>
<li><code>fabricops_kit.pipeline.shared._observe_dataframe</code></li>
<li><code>fabricops_kit.pipeline.shared._observe_lakehouse</code></li>
<li><code>fabricops_kit.pipeline.shared._observe_partition_dataframe</code></li>
<li><code>fabricops_kit.pipeline.shared._orchestration_status</code></li>
<li><code>fabricops_kit.pipeline.shared._parse_parameters</code></li>
<li><code>fabricops_kit.pipeline.shared._parse_rule_parameters</code></li>
<li><code>fabricops_kit.pipeline.shared._persist_grain_candidates</code></li>
<li><code>fabricops_kit.pipeline.shared._persist_profile_observation</code></li>
<li><code>fabricops_kit.pipeline.shared._persist_source_snapshot</code></li>
<li><code>fabricops_kit.pipeline.shared._physical_target_has_publication</code></li>
<li><code>fabricops_kit.pipeline.shared._processing_state_id</code></li>
<li><code>fabricops_kit.pipeline.shared._processing_state_rows</code></li>
<li><code>fabricops_kit.pipeline.shared._profile_column_expr</code></li>
<li><code>fabricops_kit.pipeline.shared._profile_percent_expr</code></li>
<li><code>fabricops_kit.pipeline.shared._profile_snapshot_id</code></li>
<li><code>fabricops_kit.pipeline.shared._progress_key</code></li>
<li><code>fabricops_kit.pipeline.shared._publication_receipt</code></li>
<li><code>fabricops_kit.pipeline.shared._publication_value</code></li>
<li><code>fabricops_kit.pipeline.shared._read_pipeline_run_rows</code></li>
<li><code>fabricops_kit.pipeline.shared._record_source_drift_result</code></li>
<li><code>fabricops_kit.pipeline.shared._recover_completed_source_observations</code></li>
<li><code>fabricops_kit.pipeline.shared._replace_frequency_rows</code></li>
<li><code>fabricops_kit.pipeline.shared._replace_snapshot_rows</code></li>
<li><code>fabricops_kit.pipeline.shared._row_to_dict</code></li>
<li><code>fabricops_kit.pipeline.shared._rule_review_status</code></li>
<li><code>fabricops_kit.pipeline.shared._run_orchestration_stage</code></li>
<li><code>fabricops_kit.pipeline.shared._scalar_frequency_columns</code></li>
<li><code>fabricops_kit.pipeline.shared._select_rule</code></li>
<li><code>fabricops_kit.pipeline.shared._select_table_guardrail_rule</code></li>
<li><code>fabricops_kit.pipeline.shared._selected_frequency_columns</code></li>
<li><code>fabricops_kit.pipeline.shared._show_previous_table_profile</code></li>
<li><code>fabricops_kit.pipeline.shared._source_evidence_totals</code></li>
<li><code>fabricops_kit.pipeline.shared._source_observation_signature</code></li>
<li><code>fabricops_kit.pipeline.shared._source_snapshot_keys</code></li>
<li><code>fabricops_kit.pipeline.shared._source_snapshot_state</code></li>
<li><code>fabricops_kit.pipeline.shared._spark_profile_key_candidates</code></li>
<li><code>fabricops_kit.pipeline.shared._spark_sql_helpers</code></li>
<li><code>fabricops_kit.pipeline.shared._sql_identifier</code></li>
<li><code>fabricops_kit.pipeline.shared._sql_string</code></li>
<li><code>fabricops_kit.pipeline.shared._stage_catalogue_profile_retry</code></li>
<li><code>fabricops_kit.pipeline.shared._string_value</code></li>
<li><code>fabricops_kit.pipeline.shared._summarize_dq_guardrail</code></li>
<li><code>fabricops_kit.pipeline.shared._upsert_catalogue_identities</code></li>
<li><code>fabricops_kit.pipeline.shared._validate_dq_rules</code></li>
<li><code>fabricops_kit.pipeline.shared._validated_observation_identity</code></li>
<li><code>fabricops_kit.pipeline.shared._validated_source_snapshot</code></li>
<li><code>fabricops_kit.pipeline.shared._warehouse_columns</code></li>
<li><code>fabricops_kit.pipeline.shared._warehouse_frequency_query</code></li>
<li><code>fabricops_kit.pipeline.shared._warehouse_observation_query</code></li>
<li><code>fabricops_kit.pipeline.shared._warehouse_percentile_query</code></li>
<li><code>fabricops_kit.pipeline.shared._warehouse_profile_dataframes</code></li>
<li><code>fabricops_kit.pipeline.shared._warehouse_profile_key_candidates</code></li>
<li><code>fabricops_kit.pipeline.shared._warehouse_statistical_dataframe</code></li>
<li><code>fabricops_kit.pipeline.shared._warehouse_statistical_query</code></li>
<li><code>fabricops_kit.pipeline.shared._warehouse_type_name</code></li>
<li><code>fabricops_kit.pipeline.shared._watermark_timestamp</code></li>
<li><code>fabricops_kit.pipeline.shared.build_frequency_distribution_dataframe</code></li>
<li><code>fabricops_kit.pipeline.shared.build_pipeline_audit_fields</code></li>
<li><code>fabricops_kit.pipeline.shared.build_profile_dataframe</code></li>
<li><code>fabricops_kit.pipeline.shared.canonical_pipeline_json</code></li>
<li><code>fabricops_kit.pipeline.shared.capture_profile_presentation</code></li>
<li><code>fabricops_kit.pipeline.shared.capture_source_observation</code></li>
<li><code>fabricops_kit.pipeline.shared.check_dq_runtime</code></li>
<li><code>fabricops_kit.pipeline.shared.collect_freshness_evidence</code></li>
<li><code>fabricops_kit.pipeline.shared.compare_source_snapshot_evidence</code></li>
<li><code>fabricops_kit.pipeline.shared.contract_guardrail_rows</code></li>
<li><code>fabricops_kit.pipeline.shared.current_pipeline_session</code></li>
<li><code>fabricops_kit.pipeline.shared.display_profile_presentations</code></li>
<li><code>fabricops_kit.pipeline.shared.display_table_identity</code></li>
<li><code>fabricops_kit.pipeline.shared.dq_tolerance_parameter</code></li>
<li><code>fabricops_kit.pipeline.shared.evaluate_freshness_evidence</code></li>
<li><code>fabricops_kit.pipeline.shared.execute_table_profile</code></li>
<li><code>fabricops_kit.pipeline.shared.execution_result</code></li>
<li><code>fabricops_kit.pipeline.shared.file_binding_source</code></li>
<li><code>fabricops_kit.pipeline.shared.file_participant_source</code></li>
<li><code>fabricops_kit.pipeline.shared.freshness_check_core</code></li>
<li><code>fabricops_kit.pipeline.shared.get_current_freshness_evidence</code></li>
<li><code>fabricops_kit.pipeline.shared.load_table_guardrail_rules</code></li>
<li><code>fabricops_kit.pipeline.shared.observation_rows</code></li>
<li><code>fabricops_kit.pipeline.shared.observe_full_source</code></li>
<li><code>fabricops_kit.pipeline.shared.participant_id</code></li>
<li><code>fabricops_kit.pipeline.shared.persist_pipeline_run</code></li>
<li><code>fabricops_kit.pipeline.shared.persistence_permitted</code></li>
<li><code>fabricops_kit.pipeline.shared.pipeline_guardrail_types</code></li>
<li><code>fabricops_kit.pipeline.shared.pipeline_physical_bindings</code></li>
<li><code>fabricops_kit.pipeline.shared.pipeline_profiling_policy</code></li>
<li><code>fabricops_kit.pipeline.shared.pipeline_record_content</code></li>
<li><code>fabricops_kit.pipeline.shared.pipeline_run_row</code></li>
<li><code>fabricops_kit.pipeline.shared.prepare_pipeline_execution</code></li>
<li><code>fabricops_kit.pipeline.shared.print_guardrail_result</code></li>
<li><code>fabricops_kit.pipeline.shared.print_pipeline_contract</code></li>
<li><code>fabricops_kit.pipeline.shared.profiling_completion_history</code></li>
<li><code>fabricops_kit.pipeline.shared.profiling_context_key</code></li>
<li><code>fabricops_kit.pipeline.shared.profiling_due</code></li>
<li><code>fabricops_kit.pipeline.shared.read_file_participant</code></li>
<li><code>fabricops_kit.pipeline.shared.record_profiling_outcome</code></li>
<li><code>fabricops_kit.pipeline.shared.resolve_catalogue_table_identity</code></li>
<li><code>fabricops_kit.pipeline.shared.resolve_file_participant</code></li>
<li><code>fabricops_kit.pipeline.shared.resolve_incremental_source_scope</code></li>
<li><code>fabricops_kit.pipeline.shared.resolve_physical_table_identity</code></li>
<li><code>fabricops_kit.pipeline.shared.resolve_pipeline_data_contract</code></li>
<li><code>fabricops_kit.pipeline.shared.resolve_profiled_columns</code></li>
<li><code>fabricops_kit.pipeline.shared.row_hash_expression</code></li>
<li><code>fabricops_kit.pipeline.shared.row_hash_totals</code></li>
<li><code>fabricops_kit.pipeline.shared.schedule_file_profiling</code></li>
<li><code>fabricops_kit.pipeline.shared.schedule_table_profiling</code></li>
<li><code>fabricops_kit.pipeline.shared.schema_check_core</code></li>
<li><code>fabricops_kit.pipeline.shared.select_table_guardrail_rule</code></li>
<li><code>fabricops_kit.pipeline.shared.source_drift_investigation_query</code></li>
<li><code>fabricops_kit.pipeline.shared.source_drift_requires_intervention</code></li>
<li><code>fabricops_kit.pipeline.shared.source_observation_run_id</code></li>
<li><code>fabricops_kit.pipeline.shared.source_snapshot_context</code></li>
<li><code>fabricops_kit.pipeline.shared.source_snapshot_projection</code></li>
<li><code>fabricops_kit.pipeline.shared.validate_freshness_parameters</code></li>
<li><code>fabricops_kit.pipeline.shared.validate_grain_parameters</code></li>
<li><code>fabricops_kit.pipeline.shared.validate_pipeline_id</code></li>
<li><code>fabricops_kit.pipeline.shared.validate_pipeline_profiling</code></li>
<li><code>fabricops_kit.pipeline.shared.validate_pipeline_run</code></li>
<li><code>fabricops_kit.pipeline.shared.validate_source_drift_configuration</code></li>
<li><code>fabricops_kit.pipeline.shared.validated_pipeline_processing</code></li>
<li><code>fabricops_kit.pipeline.shared.validated_processing</code></li>
<li><code>fabricops_kit.pipeline.shared.write_guardrail_result_row</code></li>
</ul>


</details>

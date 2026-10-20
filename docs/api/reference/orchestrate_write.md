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
result = orchestrate_write(
    transformed_df, sources=[source], store="Silver", schema="demo",
    table_name="orders", write_mode="overwrite", contracts=CONTRACTS,
)
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
    sources: Iterable[dict[str, Any]],
    store: str,
    schema: str | None,
    table_name: str,
    write_mode: str,
    write_parameters: dict[str, Any] | None=None,
    contracts: dict[str, Any] | None=None,
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
| `dataframe` | `Any` | Yes | `—` | Transformed Spark DataFrame to validate and publish. |
| `sources` | `Iterable[dict[str, Any]]` | Yes | `—` | Governed source results containing ``table_id``. Pass [] for a source-free target. |
| `store` | `str` | Yes | `—` | Configured destination store key. |
| `schema` | `str \| None` | Yes | `—` | Physical target schema. This keyword is required; pass None for a store without schemas. |
| `table_name` | `str` | Yes | `—` | Physical target table name. |
| `write_mode` | `str` | Yes | `—` | Notebook-facing Write mode forwarded to the internal Write stage as its governed load strategy. |
| `write_parameters` | `dict[str, Any] \| None` | No | `None` | Parameters for the selected Write mode, forwarded to the internal Write stage as ``load_strategy_parameters``. For example, SCD1 requires ``key_columns``; SCD2 requires ``key_columns`` and ``effective_column`` and may also define ``tracked_columns``. |
| `contracts` | `dict[str, Any] \| None` | No | `None` | ``widget_select_data_contract`` result used to choose Validate or Enforce publication behaviour. Both modes run the same Guardrails. |
| `repartition_by` | `int \| None` | No | `None` | Spark write partition count. |
| `grain_discovery_enabled` | `bool` | No | `True` | Whether Profile discovers candidate Grain keys for this call. False skips discovery and preserves saved candidates; contract Grain checks still run. |
| `grain_discovery_max_columns` | `int` | No | `3` | Maximum columns in a candidate key. 1 checks single columns only; 2 also checks pairs. Must be a positive integer. Wider searches can be costly. |
| `grain_discovery_max_candidates` | `int` | No | `8` | Maximum candidate keys to retain at the smallest valid key width. Must be a positive integer. Discovery stops after enough keys are found; this limit does not cap work when no valid key exists. |
| `frequency_enabled` | `bool` | No | `True` | Whether Profile calculates frequency distributions for this call. The caller controls when to enable discovery and frequency profiling. |
| `frequency_top_n` | `int \| None` | No | `5` | Maximum ranked frequency values per eligible column; None retains all. |
| `existing_mapping` | `pyspark.sql.DataFrame` | No | `None` | Previously returned Sensitive Data token mappings. Existing assignments are reused; the returned sensitive_result contains the support_mapping for the caller to persist and supply on later runs. When Engineering configures GovernanceConfig.sensitive_data_token_mapping, Enforce automatically reuses and inserts assignments in that restricted Delta store. Validate reads the store without writing it. Without that setting, mapping management remains caller-owned. Caller-owned mappings retain established identities absent from the current batch; managed mappings return only assignments used in the current batch. Do not combine a configured mapping store with existing_mapping. After consuming the prepared DataFrame and persisting the mapping, call its unpersist() method to release its cache. Failed orchestration releases it automatically. |
| `spark_session` | `object` | No | `None` | Spark session used by every stage. |
| `verbose` | `bool` | No | `True` | Print stage start, outcome, duration, and failure attribution. |
| `dq_diagnostics` | `str` | No | `'sample'` | Sample captures at most ten illustrative source records per DQ rule with exact metrics in the same aggregation. None captures metrics only. Full also returns every failure as a lazy diagnostic DataFrame. |

</div>

## Advanced examples

<div class="reference-example-usage" markdown="1">

```python
result = orchestrate_write(
    transformed_df, sources=[orders], store="Silver", schema="demo",
    table_name="curated_orders", write_mode="overwrite", contracts=CONTRACTS,
)
```

Development SCD1 with a source-free mapping table:

```python
result = orchestrate_write(
    product_mapping_df, sources=[], store="Silver", schema="demo",
    table_name="product_mapping", write_mode="scd1",
    write_parameters={"key_columns": ["product_id"]},
)
```

Discovery and frequency switches apply only when the lifecycle runs Profile.
Pass ``grain_discovery_enabled=False, frequency_enabled=False`` on routine
calls and enable either option on calls chosen by your own scheduler.

</div>

## Returns

dict
    Write identity and capability results. The top-level ``dataframe`` is
    the prepared input after Sensitive Data treatment, in both Validate
    and Enforce modes. It is the Write input, not necessarily the persisted
    target after Append, SCD1, or SCD2. ``sensitive_result`` retains its
    nested ``dataframe`` result. ``published`` is false when a Validate-mode
    contract passes without publication. ``write_metrics`` retains the
    internal Write measurements, with ``total_target_rows`` reused from
    persisted-target profiling when available. It never treats prepared
    input rows or profiled target rows as committed rows.
    ``total_duration_seconds`` measures the complete lifecycle, including
    Guardrails, metadata finalization, and profiling.

## Raises / Errors

ValueError
    If a discovery limit is not a positive integer; checked before any stage runs.
RuntimeError
    If any stage fails. Its name is reported and the original exception is
    retained as ``__cause__``.
    A Profile failure after successful Write also exposes ``published=True``,
    ``table_id``, ``write_metrics``, and ``failed_stage="Profile"`` on the
    exception. Publication and checkpoint finalization have already completed.

## Notes

<div class="reference-docstring-notes" markdown="1">

Both contract modes evaluate the same configured Guardrails using contracts
and rules resolved once per call. Absent Guardrails remain skipped in the
result fields but are omitted from stdout and orchestration_stages.
Contract-free Development prints one decision and proceeds to Write.
DQ summaries retain exact observed pass/fail counts independently of the
authored tolerance decision. Sample mode stores at most ten illustrative
source records per rule in METADATA_GUARDRAIL_RESULTS.result_payload_json;
dq_result["failed_values"] contains only those captured examples. None
suppresses examples; full returns an unbounded lazy failure DataFrame.
dq_result["dataframe"] retains lazy row tags. The top-level source/prepared
DataFrame and published target do not acquire those tags automatically.
Validate resolves the exact selected frozen candidate and records
execution_type=validate evidence for activation, including a completion
record for every covered contract after Guardrail Coverage and Processing
pass, then returns without writing. Processing uses the same strategy/parameter
validation and exact contract comparison as Enforce, rejecting invalid SCD
definitions and mismatches before recording successful validation. Validate
does not exercise the physical writer or test destination availability.
Enforce continues through Write and persisted-target Profile. Existing
metadata and Source Observation commit behaviour remains owned by
the internal Write stage. The returned ``dataframe`` is the prepared Write input,
not a reread of the persisted target; Append, SCD1, and SCD2 may produce a
different target state. Grain checks the prepared input after Sensitive Data
treatment for every strategy; it does not check existing target rows or
guarantee resulting-table uniqueness for Append, SCD1, or SCD2. SCD strategies
retain their separate business-key requirements and reject null business-key
components before staging or merging. Use a version-aware Grain
key for SCD2 history. No DataFrame is displayed or materialized for this
return value. With verbose=True, every successful execution prints a final
WRITE Summary to stdout, including Validate-only runs. Unavailable row
metrics print as ``Not available``. Reporting adds no Spark actions.

</div>

## See also

No related guides documented.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/pipeline/orchestrate_write.py:24`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline/orchestrate_write.py#L24-L293">View on GitHub</a>
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
| Live-critical dependencies | 189 |

### Release history

| Status | Version |
| --- | --- |
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
<li><code>fabricops_kit.io.shared.resolve_configured_lakehouse_table</code></li>
<li><code>fabricops_kit.io.shared.resolve_configured_warehouse_table</code></li>
<li><code>fabricops_kit.io.shared.resolve_lakehouse_table_location</code></li>
<li><code>fabricops_kit.io.shared.resolve_store</code></li>
<li><code>fabricops_kit.io.shared.resolve_warehouse_table_location</code></li>
<li><code>fabricops_kit.io.shared.write_warehouse_synapsesql</code></li>
<li><code>fabricops_kit.pipeline.check_dq.check_dq</code></li>
<li><code>fabricops_kit.pipeline.check_grain.check_grain</code></li>
<li><code>fabricops_kit.pipeline.check_guardrail_coverage._contract</code></li>
<li><code>fabricops_kit.pipeline.check_guardrail_coverage._current_activity_results</code></li>
<li><code>fabricops_kit.pipeline.check_guardrail_coverage._label</code></li>
<li><code>fabricops_kit.pipeline.check_guardrail_coverage._latest_can_continue</code></li>
<li><code>fabricops_kit.pipeline.check_guardrail_coverage._payload</code></li>
<li><code>fabricops_kit.pipeline.check_guardrail_coverage._rules</code></li>
<li><code>fabricops_kit.pipeline.check_guardrail_coverage.check_guardrail_coverage</code></li>
<li><code>fabricops_kit.pipeline.check_schema.check_schema</code></li>
<li><code>fabricops_kit.pipeline.check_sensitive_data.check_sensitive_data</code></li>
<li><code>fabricops_kit.pipeline.check_source_drift.check_source_drift</code></li>
<li><code>fabricops_kit.pipeline.pipeline_write._persist_target_processing</code></li>
<li><code>fabricops_kit.pipeline.pipeline_write._physical_processing_definition</code></li>
<li><code>fabricops_kit.pipeline.pipeline_write._source_table_ids</code></li>
<li><code>fabricops_kit.pipeline.pipeline_write._target_has_activity</code></li>
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
<li><code>fabricops_kit.pipeline.shared.add_target_audit_fields</code></li>
<li><code>fabricops_kit.pipeline.shared.build_frequency_distribution_dataframe</code></li>
<li><code>fabricops_kit.pipeline.shared.build_profile_dataframe</code></li>
<li><code>fabricops_kit.pipeline.shared.catalogue_authored_processing</code></li>
<li><code>fabricops_kit.pipeline.shared.check_dq_runtime</code></li>
<li><code>fabricops_kit.pipeline.shared.check_sensitive_data_rules</code></li>
<li><code>fabricops_kit.pipeline.shared.check_source_drift_for_target</code></li>
<li><code>fabricops_kit.pipeline.shared.commit_pipeline_write_success</code></li>
<li><code>fabricops_kit.pipeline.shared.contract_guardrail_rows</code></li>
<li><code>fabricops_kit.pipeline.shared.display_table_identity</code></li>
<li><code>fabricops_kit.pipeline.shared.dq_tolerance_parameter</code></li>
<li><code>fabricops_kit.pipeline.shared.evaluate_source_drift_guardrail</code></li>
<li><code>fabricops_kit.pipeline.shared.execute_lakehouse_processing</code></li>
<li><code>fabricops_kit.pipeline.shared.get_current_source_observation</code></li>
<li><code>fabricops_kit.pipeline.shared.grain_check_core</code></li>
<li><code>fabricops_kit.pipeline.shared.incremental_publication_scopes</code></li>
<li><code>fabricops_kit.pipeline.shared.lineage_id</code></li>
<li><code>fabricops_kit.pipeline.shared.load_table_guardrail_rules</code></li>
<li><code>fabricops_kit.pipeline.shared.observation_rows</code></li>
<li><code>fabricops_kit.pipeline.shared.persist_lineage_participation</code></li>
<li><code>fabricops_kit.pipeline.shared.pipeline_guardrail_types</code></li>
<li><code>fabricops_kit.pipeline.shared.prepare_pipeline_execution</code></li>
<li><code>fabricops_kit.pipeline.shared.print_guardrail_result</code></li>
<li><code>fabricops_kit.pipeline.shared.print_pipeline_contract</code></li>
<li><code>fabricops_kit.pipeline.shared.record_contract_validation</code></li>
<li><code>fabricops_kit.pipeline.shared.resolve_active_data_contract</code></li>
<li><code>fabricops_kit.pipeline.shared.resolve_catalogue_table_identity</code></li>
<li><code>fabricops_kit.pipeline.shared.resolve_data_contract_version</code></li>
<li><code>fabricops_kit.pipeline.shared.resolve_physical_table_identity</code></li>
<li><code>fabricops_kit.pipeline.shared.resolve_pipeline_data_contract</code></li>
<li><code>fabricops_kit.pipeline.shared.resolve_profiled_columns</code></li>
<li><code>fabricops_kit.pipeline.shared.resolve_scd1_business_columns</code></li>
<li><code>fabricops_kit.pipeline.shared.resolve_scd2_tracked_columns</code></li>
<li><code>fabricops_kit.pipeline.shared.resolve_table_processing_definition</code></li>
<li><code>fabricops_kit.pipeline.shared.resolve_target_audit_fields</code></li>
<li><code>fabricops_kit.pipeline.shared.schema_check_core</code></li>
<li><code>fabricops_kit.pipeline.shared.select_table_guardrail_rule</code></li>
<li><code>fabricops_kit.pipeline.shared.stage_pipeline_write_observations</code></li>
<li><code>fabricops_kit.pipeline.shared.validate_grain_parameters</code></li>
<li><code>fabricops_kit.pipeline.shared.validated_processing</code></li>
<li><code>fabricops_kit.pipeline.shared.write_guardrail_result_row</code></li>
</ul>


</details>

# `pipeline_write`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-live reference-lifecycle-chip-prominent">Live</span>
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-live reference-lifecycle-chip-prominent">Live since 0.2.0</span>
<span class="reference-chip reference-chip-muted">Public function</span>
</p>

> This function is part of the supported FabricOps public contract. Changes to its signature, behaviour, public export, or Live-critical dependencies require Live-contract review.

Publish one governed pipeline target through its configured Fabric store.

<div class="reference-docstring-intro" markdown="1">

``pipeline_write`` is the governed pipeline-orchestration equivalent of
:func:`write_lakehouse_table` and :func:`write_warehouse_table`. Describe
the governed target once; FabricOps resolves its canonical identity and
configured store, resolves governed processing from the selected or active
Data Contract, and selects the appropriate physical publication path. It commits
Lineage and Source Observation metadata only after publication succeeds.

</div>

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/pipeline/pipeline_write.py:336`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline/pipeline_write.py#L336-L747">View on GitHub</a>
</div>

<p class="reference-catalogue-item-meta reference-catalogue-item-badges">
<span class="reference-chip">Public Starter Kit function</span>
<span class="reference-chip">02B_incremental_append_pipeline</span>
</p>

**Used in notebooks:** `02B_incremental_append_pipeline`

## Usage notes

Use this as part of the standard Starter Kit pipeline flow. Pipeline helpers prepare, validate, profile, write, and document pipeline data in a consistent way across notebooks.

For profiling-related pipeline functions, the output captures the important details and profile of the data so downstream users can review the dataset consistently instead of relying on one-off summaries.


## Signature

<div class="reference-api-definition" markdown="1">

```python
def pipeline_write(
    df,
    store: str | None=None,
    schema: str | None=None,
    table_name: str | None=None,
    table_id: str | None=None,
    load_strategy: str | None=None,
    load_strategy_parameters: dict[str, Any] | None=None,
    source_table_ids: list[str] | tuple[str, ...] | None=None,
    repartition_by=None,
    options: dict[str, Any] | None=None,
    spark_session=None,
    verbose: bool=True,
) -> dict[str, str]:
```

</div>

## Example usage

<div class="reference-example-usage" markdown="1">

Publish without knowing whether ``unified`` is a Lakehouse or Warehouse:

>>> result = pipeline_write(
...     prepared_df, store="Silver", schema="demo",
...     table_name="curated_orders",
...     source_table_ids=[orders_result["table_id"]],
... )
>>> result["table_id"]
'lakehouse:unified:demo:curated_orders'

Development may propose processing, without bypassing contract authority:

>>> pipeline_write(
...     prepared_df, store="Silver", schema="demo",
...     table_name="curated_orders", load_strategy="overwrite",
...     source_table_ids=[orders_result["table_id"]],
... )

</div>

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `df` | `pyspark.sql.DataFrame` | Yes | Prepared target DataFrame after explicit target checks have passed. |
| `store` | `str \| None` | No | Configured store key. Supply it with ``table_name`` and optional ``schema`` instead of ``table_id``. |
| `schema` | `str \| None` | No | Physical target schema when the configured store uses schemas. |
| `table_name` | `str \| None` | No | Physical target table name. Required with ``store`` when ``table_id`` is omitted. |
| `table_id` | `str \| None` | No | Canonical registered target identity. This identity form is mutually exclusive with ``store``, ``schema``, and ``table_name``. |
| `load_strategy` | `str \| None` | No | Development-authored processing proposal. Selected or frozen contract validation applies in Development, and the active approved Data Contract remains authoritative in Production. |
| `load_strategy_parameters` | `dict[str, Any] \| None` | No | Development-authored strategy parameters, such as key, effective, tracked, or partition columns, subject to contract validation. |
| `source_table_ids` | `list[str] \| tuple[str, ...] \| None` | No | Canonical identities of the exact governed sources that feed this target publication. Supply identities returned by ``pipeline_read``. FabricOps requires this explicit association because activity-wide reads and Spark transformation plans cannot reliably identify which source subset produced a particular target DataFrame. |
| `repartition_by` | `int or str or list[str] or tuple[str, ...]` | No | Optional Spark repartitioning passed to simple physical writes. |
| `options` | `dict[str, Any] \| None` | No | Additional physical writer options for append or overwrite publication. |
| `spark_session` | `object` | No | Spark session used for write-side metadata persistence. Supply the active Fabric notebook session explicitly when available. |
| `verbose` | `bool` | No | Whether to print one concise orchestration message showing the resolved Fabric store type, physical table identity, governed strategy, and selected foundational writer or governed SCD publication path. This explains hidden routing without exposing implementation plumbing. |

## Returns

A small result containing the canonical target table_id.

## Raises / Errors

ValueError
    If identity inputs conflict or are incomplete, ``source_table_ids`` is
    missing or invalid, governed processing is invalid, ownership does not
    match, the target store is unsupported, incremental input is paired
    with whole-table overwrite, or an incremental append bootstrap finds
    an already-populated target without committed source-to-target state.

## Notes

<div class="reference-docstring-notes" markdown="1">

The governed orchestration performs these mechanical steps:

1. Resolve the canonical target ``table_id``.
2. Resolve the configured physical target identity.
3. Resolve the selected or active Data Contract.
4. Resolve the governed load strategy and parameters.
5. Resolve processing scope.
6. Apply FabricOps target audit fields.
7. Validate target notebook ownership.
8. Detect whether this activity already produced target rows.
9. Perform append/overwrite or dedicated SCD processing only when the
   activity is not already represented in the physical target.
10. Persist the resolved target load strategy and parameters on the
    table-level ``METADATA_DATA_CATALOGUE`` row.
11. Only after physical and Catalogue success, idempotently commit target
    Lineage and accepted Source Observation/write-success metadata.
12. Return a small publication result with no hidden profiling state.

Callers do not provide a store type, manually resolve ``table_id``, choose
a Lakehouse versus Warehouse writer, construct processing scope or success
context, or manually commit Lineage or Source Observation metadata. Callers
provide only the canonical identities of the sources that actually feed
this target, rather than internal read or preparation dictionaries. This
keeps multiple target writes in one activity exact and independent.

Same-activity retries use the target's persisted ``_activity_id`` audit
field to detect a row-producing publication and skip its physical mutation.
Catalogue processing, Lineage, and accepted Source Observation metadata are
idempotent and replayed on every retry. Empty append, empty overwrite,
partition-removal-only overwrite, and true SCD no-op operations may leave
no activity marker; repeating those operations is safe. Changing the
participating source set represents a different logical publication and
therefore requires a new activity rather than reuse of the current one.
Lakehouse SCD2 closes changed rows and inserts their replacement current
versions in one Delta ``MERGE`` so an activity marker cannot represent a
partially applied two-step history mutation. Warehouse SCD2 retains its
existing SQL transaction boundary.

Before physical publication, target-specific Source Observation evidence
is durably staged with ``observation_status='observed'``. If a scheduled
activity terminates after target rows materialize but before finalization,
the next activity verifies the prior target ``_activity_id``, promotes that
staged evidence idempotently, and calculates incremental work from the
recovered committed baseline. Evidence for another target is not promoted.

A first incremental append has no committed baseline and therefore reads a
complete bootstrap scope. FabricOps permits that bootstrap only for a new
or empty physical target. A populated target fails before publication so
missing metadata cannot silently duplicate all source rows. SCD1 and SCD2
bootstraps continue through their existing keyed, idempotent merge paths.

A removed source partition is actionable incremental work even though its
input DataFrame contains no rows for that partition. FabricOps permits the
removal only when governed partition-scoped overwrite can include the
removed value in ``replaceWhere`` and clear stale target rows. Other target
strategies, or mismatched source and target partition columns, fail before
publication and therefore do not commit the removal baseline.

With ``verbose=True``, a simple Lakehouse overwrite reports a line such as
``FabricOps Write → Lakehouse table 'unified.demo.curated_orders' → overwrite → write_lakehouse_table``.

This function does not perform transformations, schema checks, DQ checks,
Sensitive Data Guardrails, Source Drift, or profiling. These remain
explicit notebook engineering and governance steps. ``pipeline_write`` publishes governed
table targets only. Raw Lakehouse Files do not have a canonical FabricOps
``table_id``; direct file-output concerns, if supported in future, belong
outside this governed table orchestration API.

</div>

## See also

No related guides documented.


<details>
<summary>Maintainer architecture details</summary>

## Contract impact

| Property | Value |
| --- | --- |
| Lifecycle | <span class="reference-chip reference-lifecycle-chip reference-lifecycle-live">Live</span> |
| Live since | 0.2.0 |
| Discontinued in | — |
| Contract classification | Live public function |
| Contract risk | Live |
| Live-critical dependencies | 82 |

### Release history

| Status | Version |
| --- | --- |
| Live | 0.2.0 |

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
<li><code>fabricops_kit.config.shared.build_table_id</code></li>
<li><code>fabricops_kit.config.shared.get_audit_timezone</code></li>
<li><code>fabricops_kit.config.shared.get_current_audit_timestamp</code></li>
<li><code>fabricops_kit.config.shared.get_default_fabric_context</code></li>
<li><code>fabricops_kit.config.shared.get_store</code></li>
<li><code>fabricops_kit.config.shared.is_table_not_found_error</code></li>
<li><code>fabricops_kit.config.shared.resolve_fabric_context</code></li>
<li><code>fabricops_kit.config.shared.resolve_runtime_context</code></li>
<li><code>fabricops_kit.config.shared.stable_metadata_id</code></li>
<li><code>fabricops_kit.data_contract.scheduled_refresh._fabric_schedules_json</code></li>
<li><code>fabricops_kit.data_contract.scheduled_refresh._time_value</code></li>
<li><code>fabricops_kit.data_contract.scheduled_refresh.canonical_scheduled_refresh</code></li>
<li><code>fabricops_kit.data_contract.scheduled_refresh.discover_scheduled_refresh</code></li>
<li><code>fabricops_kit.data_contract.scheduled_refresh.normalize_scheduled_refresh</code></li>
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
<li><code>fabricops_kit.pipeline.pipeline_write._delta_literal</code></li>
<li><code>fabricops_kit.pipeline.pipeline_write._persist_target_processing</code></li>
<li><code>fabricops_kit.pipeline.pipeline_write._replace_where</code></li>
<li><code>fabricops_kit.pipeline.pipeline_write._source_table_ids</code></li>
<li><code>fabricops_kit.pipeline.pipeline_write._target_has_activity</code></li>
<li><code>fabricops_kit.pipeline.pipeline_write._target_has_rows</code></li>
<li><code>fabricops_kit.pipeline.pipeline_write._validate_target_writer_ownership</code></li>
<li><code>fabricops_kit.pipeline.pipeline_write._warehouse_target_exists</code></li>
<li><code>fabricops_kit.pipeline.pipeline_write._write_scope</code></li>
<li><code>fabricops_kit.pipeline.pipeline_write._writer_scheduled_refresh</code></li>
<li><code>fabricops_kit.pipeline.shared._contract_payload</code></li>
<li><code>fabricops_kit.pipeline.shared._merge_source_observation_records</code></li>
<li><code>fabricops_kit.pipeline.shared._row_to_dict</code></li>
<li><code>fabricops_kit.pipeline.shared._sql_literal</code></li>
<li><code>fabricops_kit.pipeline.shared.add_target_audit_fields</code></li>
<li><code>fabricops_kit.pipeline.shared.catalogue_authored_processing</code></li>
<li><code>fabricops_kit.pipeline.shared.commit_pipeline_write_success</code></li>
<li><code>fabricops_kit.pipeline.shared.execute_lakehouse_processing</code></li>
<li><code>fabricops_kit.pipeline.shared.incremental_publication_scopes</code></li>
<li><code>fabricops_kit.pipeline.shared.lineage_id</code></li>
<li><code>fabricops_kit.pipeline.shared.persist_lineage_participation</code></li>
<li><code>fabricops_kit.pipeline.shared.resolve_active_data_contract</code></li>
<li><code>fabricops_kit.pipeline.shared.resolve_catalogue_table_identity</code></li>
<li><code>fabricops_kit.pipeline.shared.resolve_data_contract_version</code></li>
<li><code>fabricops_kit.pipeline.shared.resolve_physical_table_identity</code></li>
<li><code>fabricops_kit.pipeline.shared.resolve_scd1_business_columns</code></li>
<li><code>fabricops_kit.pipeline.shared.resolve_scd2_tracked_columns</code></li>
<li><code>fabricops_kit.pipeline.shared.resolve_table_processing_definition</code></li>
<li><code>fabricops_kit.pipeline.shared.resolve_target_audit_fields</code></li>
<li><code>fabricops_kit.pipeline.shared.stage_pipeline_write_observations</code></li>
<li><code>fabricops_kit.pipeline.shared.validated_processing</code></li>
</ul>


</details>

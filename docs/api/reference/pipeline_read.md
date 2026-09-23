# `pipeline_read`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-live reference-lifecycle-chip-prominent">Live</span>
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-live reference-lifecycle-chip-prominent">Live since 0.2.0</span>
<span class="reference-chip reference-chip-muted">Public function</span>
</p>

> This function is part of the supported FabricOps public contract. Changes to its signature, behaviour, public export, or Live-critical dependencies require Live-contract review.

Read one governed pipeline source through its configured Fabric store.

<div class="reference-docstring-intro" markdown="1">

``pipeline_read`` is the governed pipeline-orchestration equivalent of the
foundational :func:`read_lakehouse_table`, :func:`read_warehouse_table`,
and :func:`read_warehouse_query` readers. Describe the governed source
once; FabricOps resolves its identity and configured store, selects the
physical reader, and returns the data needed by the notebook. Callers do
not supply a store type, resolve a canonical table identity first, or
choose between Lakehouse and Warehouse table readers.

</div>

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/pipeline/pipeline_read.py:51`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline/pipeline_read.py#L51-L377">View on GitHub</a>
</div>

<p class="reference-catalogue-item-meta reference-catalogue-item-badges">
<span class="reference-chip">Public Starter Kit function</span>
<span class="reference-chip">02_pipeline</span>
<span class="reference-chip">02B_incremental_append_pipeline</span>
</p>

**Used in notebooks:** `02_pipeline`, `02B_incremental_append_pipeline`

## Usage notes

Use this as part of the standard Starter Kit pipeline flow. Pipeline helpers prepare, validate, profile, write, and document pipeline data in a consistent way across notebooks.

For profiling-related pipeline functions, the output captures the important details and profile of the data so downstream users can review the dataset consistently instead of relying on one-off summaries.


## Signature

<div class="reference-api-definition" markdown="1">

```python
def pipeline_read(
    store: str | None=None,
    schema: str | None=None,
    table_name: str | None=None,
    table_id: str | None=None,
    query: str | None=None,
    read_mode: str='full',
    target_table_id: str | None=None,
    spark_session=None,
    verbose: bool=True,
) -> dict[str, Any]:
```

</div>

## Example usage

<div class="reference-example-usage" markdown="1">

Read a governed table without knowing whether ``source`` resolves to a
Lakehouse or Warehouse:

>>> result = pipeline_read(
...     store="Bronze",
...     schema="demo",
...     table_name="orders",
... )
>>> orders_df = result["dataframe"]
>>> orders_table_id = result["table_id"]

Read only work not yet committed for one target:

>>> result = pipeline_read(
...     store="Bronze", schema="demo", table_name="orders",
...     read_mode="incremental", target_table_id=target_table_id,
... )
>>> result["should_process"]
True

Read a governed Warehouse source through project-owned SQL:

>>> result = pipeline_read(
...     store="Gold",
...     schema="demo",
...     table_name="order_history",
...     query='''
...         SELECT customer_id, COUNT(*) AS order_count
...         FROM demo.order_history
...         GROUP BY customer_id
...     ''',
... )
>>> history_df = result["dataframe"]
>>> result["is_query"]
True

The query result is marked as derived so later notebook logic can use
``profile_table(dataframe=history_df)`` without registering it as the
complete physical ``demo.order_history`` source table.

</div>

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `store` | `str \| None` | No | Configured source store key, such as ``"source"`` or ``"product"``. Supply it with ``table_name`` and optional ``schema`` instead of ``table_id``. |
| `schema` | `str \| None` | No | Physical source schema, when the configured store uses schemas. |
| `table_name` | `str \| None` | No | Physical source table name. Required with ``store`` when ``table_id`` is omitted. ``store``, optional ``schema``, and ``table_name`` form one identity form. |
| `table_id` | `str \| None` | No | Canonical registered source identity. This is the alternative identity form and is mutually exclusive with ``store``, ``schema``, and ``table_name``. |
| `query` | `str \| None` | No | Read-only SQL for a configured Warehouse source. The supplied source identity remains the governed source participant even when the result is a projection, filter, join, or aggregation. FabricOps does not infer arbitrary source identity by parsing SQL. A query may accompany either physical coordinates or ``table_id`` when the resolved store is a Warehouse. |
| `read_mode` | `str` | No | Explicit source read behaviour. ``full`` preserves the complete-source read. ``incremental`` resolves unconsumed work from the last Source Observation committed for this exact source-to-target relationship. |
| `target_table_id` | `str \| None` | No | Canonical governed target being prepared. It is accepted for both read modes so target flows can use one consistent call shape, and is required when ``read_mode="incremental"``. |
| `spark_session` | `object` | No | Spark session forwarded to the selected foundational reader instead of relying on notebook-global ``spark``. |
| `verbose` | `bool` | No | Whether to print one concise orchestration message showing the resolved Fabric store type, physical table identity, and selected foundational reader. This makes the hidden routing understandable without exposing workspace IDs, SQL text, contract payloads, or runtime plumbing. |

## Returns

DataFrame, canonical source table_id, read mode, custom-query and contract signals, has_data/should_process, and a compact resolved scope summary.

## Raises / Errors

ValueError
    If identity inputs conflict or are incomplete, the source is not
    registered, its configured store kind is unsupported, or a query is
    supplied for a Lakehouse source, incremental mode has no target, or
    project-owned Warehouse SQL is combined with incremental mode.

## Notes

<div class="reference-docstring-notes" markdown="1">

The governed orchestration performs these mechanical steps:

1. Resolve the canonical source ``table_id``.
2. Resolve the configured physical source identity.
3. Infer whether that configured source is a Lakehouse or Warehouse.
4. For incremental reads, observe the complete physical source, resolve the
   last committed state for the exact target, and derive watermark or
   changed-partition scope. A missing baseline deterministically bootstraps
   with a complete read.
5. Select and call ``read_lakehouse_table``, ``read_warehouse_table``, or
   framework-owned ``read_warehouse_query`` pushdown.
6. Capture transient current-run Source Observation state without advancing
   accepted progress. Only successful target publication commits it.
7. Return the DataFrame, explicit ``table_id``, and small source metadata
   required by the notebook.

Higher-level governed pipeline code normally uses ``pipeline_read``.
Foundational readers remain available for direct lower-level or
general-purpose Fabric reads that do not need pipeline orchestration.
``pipeline_read`` orchestrates governed table sources only. Raw Lakehouse
Files do not have a canonical ``table_id`` and should continue to use the
foundational CSV, Excel, JSON, or Parquet readers directly.

Incremental Warehouse reads reject caller-owned ``query`` SQL because
FabricOps cannot safely compose arbitrary SQL with its target-specific
progress predicate. Source Drift remains a separate compatibility check;
incremental scope answers only what this target has not consumed.

This function does not execute Freshness, Source Drift, Schema, DQ, or
Sensitive Data checks. It also does not profile
data, transform rows, or write a pipeline target. Those meaningful
engineering decisions remain explicit in ``02_pipeline`` and
``02B_incremental_append_pipeline``.

With ``verbose=True``, a Warehouse table read reports a line such as
``FabricOps Read → Warehouse table 'product.demo.orders' → read_warehouse_table``.

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
| Live-critical dependencies | 73 |

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
<li><code>fabricops_kit.pipeline.pipeline_read._filter_lakehouse_incremental</code></li>
<li><code>fabricops_kit.pipeline.pipeline_read._warehouse_incremental_query</code></li>
<li><code>fabricops_kit.pipeline.shared._catalogue_value</code></li>
<li><code>fabricops_kit.pipeline.shared._compact_rows</code></li>
<li><code>fabricops_kit.pipeline.shared._contract_payload</code></li>
<li><code>fabricops_kit.pipeline.shared._identifier</code></li>
<li><code>fabricops_kit.pipeline.shared._is_active_guardrail_rule</code></li>
<li><code>fabricops_kit.pipeline.shared._latest_source_target_observation</code></li>
<li><code>fabricops_kit.pipeline.shared._max_column_value</code></li>
<li><code>fabricops_kit.pipeline.shared._merge_source_observation_records</code></li>
<li><code>fabricops_kit.pipeline.shared._observe_dataframe</code></li>
<li><code>fabricops_kit.pipeline.shared._observe_lakehouse</code></li>
<li><code>fabricops_kit.pipeline.shared._parse_rule_parameters</code></li>
<li><code>fabricops_kit.pipeline.shared._physical_target_has_activity</code></li>
<li><code>fabricops_kit.pipeline.shared._progress_key</code></li>
<li><code>fabricops_kit.pipeline.shared._recover_completed_source_observations</code></li>
<li><code>fabricops_kit.pipeline.shared._resolve_data_contract_version</code></li>
<li><code>fabricops_kit.pipeline.shared._row_to_dict</code></li>
<li><code>fabricops_kit.pipeline.shared._rule_review_status</code></li>
<li><code>fabricops_kit.pipeline.shared._select_table_guardrail_rule</code></li>
<li><code>fabricops_kit.pipeline.shared._string_value</code></li>
<li><code>fabricops_kit.pipeline.shared._warehouse_observation_query</code></li>
<li><code>fabricops_kit.pipeline.shared.capture_source_observation</code></li>
<li><code>fabricops_kit.pipeline.shared.catalogue_authored_processing</code></li>
<li><code>fabricops_kit.pipeline.shared.contract_guardrail_rows</code></li>
<li><code>fabricops_kit.pipeline.shared.load_table_guardrail_rules</code></li>
<li><code>fabricops_kit.pipeline.shared.observation_rows</code></li>
<li><code>fabricops_kit.pipeline.shared.resolve_active_data_contract</code></li>
<li><code>fabricops_kit.pipeline.shared.resolve_catalogue_table_identity</code></li>
<li><code>fabricops_kit.pipeline.shared.resolve_freshness_observation_column</code></li>
<li><code>fabricops_kit.pipeline.shared.resolve_incremental_observation_columns</code></li>
<li><code>fabricops_kit.pipeline.shared.resolve_incremental_source_scope</code></li>
<li><code>fabricops_kit.pipeline.shared.resolve_physical_table_identity</code></li>
<li><code>fabricops_kit.pipeline.shared.resolve_pipeline_data_contract</code></li>
<li><code>fabricops_kit.pipeline.shared.resolve_source_drift_observation_columns</code></li>
<li><code>fabricops_kit.pipeline.shared.select_table_guardrail_rule</code></li>
<li><code>fabricops_kit.pipeline.shared.set_current_source_observation</code></li>
</ul>


</details>

# `pipeline_read`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-live reference-lifecycle-chip-prominent">Live</span>
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-live reference-lifecycle-chip-prominent">Live since 0.2.0</span>
</p>

> This function is part of the supported FabricOps public contract. Changes to its signature, behaviour, public export, or Live-critical dependencies require Live-contract review.

Read one governed pipeline source through its configured Fabric store.


## Usage notes

Use for an explicit full source read or a target-aware incremental source read.


## Example usage

<div class="reference-example-usage" markdown="1">

```python
source = pipeline_read(store="Bronze", schema="demo", table_name="orders")
```

</div>


<details class="reference-signature-details" markdown="1">
<summary>Signature</summary>

## Signature

<div class="reference-api-definition" markdown="1">

```python
def pipeline_read(
    *,
    store: str | None=None,
    schema: str | None=None,
    table_name: str | None=None,
    table_id: str | None=None,
    query: str | None=None,
    read_mode: str='full',
    read_parameters: dict[str, Any] | None=None,
    target_table_id: str | None=None,
    verbose: bool=True,
    context=None,
) -> dict[str, Any]:
```

</div>

</details>

## Parameters

Required describes the Python signature. An optional parameter may still be needed for the selected mode or identity form; see its description. `—` means no signature default.

<div class="reference-input-table" markdown="1">

| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `store` | `str \| None` | No | `None` | Configured source store key, such as ``"source"`` or ``"product"``. Supply it with ``table_name`` and optional ``schema`` instead of ``table_id``. |
| `schema` | `str \| None` | No | `None` | Physical source schema, when the configured store uses schemas. |
| `table_name` | `str \| None` | No | `None` | Physical source table name. Required with ``store`` when ``table_id`` is omitted. ``store``, optional ``schema``, and ``table_name`` form one identity form. |
| `table_id` | `str \| None` | No | `None` | Canonical registered source identity. This is the alternative identity form and is mutually exclusive with ``store``, ``schema``, and ``table_name``. |
| `query` | `str \| None` | No | `None` | Read-only SQL for a configured Warehouse source in full mode only; incremental mode rejects caller-owned SQL. The supplied source identity remains the governed source participant even when the result is a projection, filter, join, or aggregation. FabricOps does not infer arbitrary source identity by parsing SQL. A query may accompany either physical coordinates or ``table_id`` when the resolved store is a Warehouse. |
| `read_mode` | `str` | No | `'full'` | Explicit source read behaviour. ``full`` preserves the complete-source read. ``incremental`` resolves unconsumed work from the last Source Observation committed for this exact source-to-target relationship. |
| `read_parameters` | `dict[str, Any] \| None` | No | `None` | Incremental read configuration. Supports only watermark_column. If a Data Contract is selected, its watermark must match the requested one. For incremental mode, provide ``{"watermark_column": "modified_at"}`` when no selected contract supplies the watermark. None is valid only when the selected mode and contract provide the required configuration. |
| `target_table_id` | `str \| None` | No | `None` | Canonical governed target being prepared. It is accepted for both read modes so target flows can use one consistent call shape, and is required when ``read_mode="incremental"``. |
| `verbose` | `bool` | No | `True` | Whether to print one concise orchestration message showing the resolved Fabric store type, physical table identity, and selected foundational reader. This makes the hidden routing understandable without exposing workspace IDs, SQL text, contract payloads, or runtime plumbing. |
| `context` | `dict` | No | `None` | Call-scoped resolved contracts, rules, and Catalogue identities. |

</div>

## Advanced examples

<div class="reference-example-usage" markdown="1">

Read a governed table without knowing whether ``source`` resolves to a
Lakehouse or Warehouse:

```python
result = pipeline_read(
    store="Bronze",
    schema="demo",
    table_name="orders",
)
orders_df = result["dataframe"]
orders_table_id = result["table_id"]
```

Read only work not yet committed for one target:

```python
result = pipeline_read(
    store="Bronze", schema="demo", table_name="orders",
    read_mode="incremental", target_table_id=target_table_id,
)
result["should_process"]
```

```text
True
```

Read a governed Warehouse source through project-owned SQL:

```python
result = pipeline_read(
    store="Gold",
    schema="demo",
    table_name="order_history",
    query='''
        SELECT customer_id, COUNT(*) AS order_count
        FROM demo.order_history
        GROUP BY customer_id
    ''',
)
history_df = result["dataframe"]
result["is_query"]
```

```text
True
```

The query result is marked as derived so later notebook logic can use
``profile_table(dataframe=history_df)`` without registering it as the
complete physical ``demo.order_history`` source table.

</div>

## Returns

dict
    ``read_metrics`` contains ``rows_read`` (zero for a known empty
    incremental scope, otherwise None) and ``columns`` from schema metadata.
    No count is triggered for reporting.
    A deliberately small result with these fields:

    - ``dataframe``: the Spark DataFrame returned by the selected
      foundational Fabric I/O reader.
    - ``table_id``: the canonical identity of the governed physical source.
    - ``is_query``: whether ``dataframe`` is a custom Warehouse query
      result rather than the complete physical table.
    - ``has_contract``: whether an workspace_id-selected immutable Data
      Contract applies. The contract record itself is not exposed.
    - ``read_mode``: the explicit source read mode.
    - ``has_data`` and ``should_process``: whether this read contributes
      unconsumed work. Full reads return ``True`` without triggering a count.
    - ``scope``: a compact summary of the resolved full, bootstrap, or
      watermark scope; no metadata rows are exposed.

## Raises / Errors

ValueError
    If identity inputs conflict or are incomplete, the source is not
    registered, its configured store kind is unsupported, or a query is
    supplied for a Lakehouse source, incremental mode has no target, or
    project-owned Warehouse SQL is combined with incremental mode.
RuntimeError
    If a different source state is already awaiting publication for this
    source and target. Finish or retry that Read's prepared batch before
    reading newer data. The rejected Read preserves the pending checkpoint.

## Behavior and scope

<div class="reference-docstring-intro" markdown="1">

Spark is resolved automatically from the existing execution session.
No session is created; Spark-dependent work raises
``RuntimeError`` when no session is available.

``pipeline_read`` is the governed pipeline-orchestration equivalent of the
foundational :func:`read_lakehouse_table`, :func:`read_warehouse_table`,
and :func:`read_warehouse_query` readers. Describe the governed source
once; FabricOps resolves its identity and configured store, selects the
physical reader, and returns the data needed by the notebook. Callers do
not supply a store type, resolve a canonical table identity first, or
choose between Lakehouse and Warehouse table readers.

</div>

## See also

No related guides documented.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/pipeline/pipeline_read.py:111`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline/pipeline_read.py#L111-L486">View on GitHub</a>
</div>


<details class="reference-implementation-details" markdown="1">
<summary>Maintainer architecture details</summary>

The governed orchestration performs these mechanical steps:

1. Resolve the canonical source ``table_id``.
2. Resolve the configured physical source identity.
3. Infer whether that configured source is a Lakehouse or Warehouse.
4. For incremental reads, observe the complete physical source, resolve the
   last committed watermark for the exact target, and read rows strictly
   after it and at or below the observed upper watermark. A missing baseline
   bootstraps through that same observed upper bound, retaining null-watermark
   rows. Rows arriving above the observed bound wait for the next run.
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

Complete Read, Transform and Write for a pending incremental batch before
reading a newer source state for the same target in this pipeline run. Re-reading
identical state is allowed. A Write already in progress freezes its own
observation snapshot, allowing the next Read without changing that checkpoint.

This function does not execute Freshness, Source Drift, Schema, DQ, or
Sensitive Data checks. It also does not profile
data, transform rows, or write a pipeline target. Those meaningful
engineering decisions remain explicit in ``02_pipeline`` and the
optional processing-mode Guided Demo scenarios.

With ``verbose=True``, a Warehouse table read reports a line such as
``FabricOps Read → Warehouse table 'product.demo.orders' → read_warehouse_table``.

## Contract impact

| Property | Value |
| --- | --- |
| Lifecycle | <span class="reference-chip reference-lifecycle-chip reference-lifecycle-live">Live</span> |
| Live since | 0.2.0 |
| Discontinued in | — |
| Contract classification | Live public function |
| Contract risk | Live |
| Live-critical dependencies | 95 |

### Release history

| Status | Version |
| --- | --- |
| Live | 0.2.0 |
| Live | 0.2.5 |

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
<li><code>fabricops_kit.io.shared.resolve_warehouse_name</code></li>
<li><code>fabricops_kit.io.shared.resolve_warehouse_table_location</code></li>
<li><code>fabricops_kit.pipeline.pipeline_read._filter_lakehouse_incremental</code></li>
<li><code>fabricops_kit.pipeline.pipeline_read._resolve_requested_incremental_columns</code></li>
<li><code>fabricops_kit.pipeline.pipeline_read._warehouse_incremental_query</code></li>
<li><code>fabricops_kit.pipeline.pipeline_read._warehouse_watermark_literal</code></li>
<li><code>fabricops_kit.pipeline.shared._catalogue_value</code></li>
<li><code>fabricops_kit.pipeline.shared._coerce_datetime</code></li>
<li><code>fabricops_kit.pipeline.shared._compact_rows</code></li>
<li><code>fabricops_kit.pipeline.shared._compact_value</code></li>
<li><code>fabricops_kit.pipeline.shared._contract_payload</code></li>
<li><code>fabricops_kit.pipeline.shared._ensure_unambiguous_source_observation</code></li>
<li><code>fabricops_kit.pipeline.shared._identifier</code></li>
<li><code>fabricops_kit.pipeline.shared._is_active_guardrail_rule</code></li>
<li><code>fabricops_kit.pipeline.shared._latest_source_target_observation</code></li>
<li><code>fabricops_kit.pipeline.shared._max_column_value</code></li>
<li><code>fabricops_kit.pipeline.shared._merge_source_observation_records</code></li>
<li><code>fabricops_kit.pipeline.shared._observe_dataframe</code></li>
<li><code>fabricops_kit.pipeline.shared._observe_lakehouse</code></li>
<li><code>fabricops_kit.pipeline.shared._observe_partition_dataframe</code></li>
<li><code>fabricops_kit.pipeline.shared._parse_rule_parameters</code></li>
<li><code>fabricops_kit.pipeline.shared._physical_target_has_publication</code></li>
<li><code>fabricops_kit.pipeline.shared._processing_state_id</code></li>
<li><code>fabricops_kit.pipeline.shared._processing_state_rows</code></li>
<li><code>fabricops_kit.pipeline.shared._progress_key</code></li>
<li><code>fabricops_kit.pipeline.shared._publication_receipt</code></li>
<li><code>fabricops_kit.pipeline.shared._recover_completed_source_observations</code></li>
<li><code>fabricops_kit.pipeline.shared._row_to_dict</code></li>
<li><code>fabricops_kit.pipeline.shared._rule_review_status</code></li>
<li><code>fabricops_kit.pipeline.shared._select_table_guardrail_rule</code></li>
<li><code>fabricops_kit.pipeline.shared._source_observation_signature</code></li>
<li><code>fabricops_kit.pipeline.shared._string_value</code></li>
<li><code>fabricops_kit.pipeline.shared._validated_observation_identity</code></li>
<li><code>fabricops_kit.pipeline.shared._warehouse_observation_query</code></li>
<li><code>fabricops_kit.pipeline.shared._watermark_timestamp</code></li>
<li><code>fabricops_kit.pipeline.shared.build_pipeline_audit_fields</code></li>
<li><code>fabricops_kit.pipeline.shared.capture_source_observation</code></li>
<li><code>fabricops_kit.pipeline.shared.catalogue_authored_processing</code></li>
<li><code>fabricops_kit.pipeline.shared.contract_guardrail_rows</code></li>
<li><code>fabricops_kit.pipeline.shared.load_table_guardrail_rules</code></li>
<li><code>fabricops_kit.pipeline.shared.observation_rows</code></li>
<li><code>fabricops_kit.pipeline.shared.persistence_permitted</code></li>
<li><code>fabricops_kit.pipeline.shared.resolve_catalogue_table_identity</code></li>
<li><code>fabricops_kit.pipeline.shared.resolve_freshness_observation_column</code></li>
<li><code>fabricops_kit.pipeline.shared.resolve_incremental_observation_columns</code></li>
<li><code>fabricops_kit.pipeline.shared.resolve_incremental_source_scope</code></li>
<li><code>fabricops_kit.pipeline.shared.resolve_physical_table_identity</code></li>
<li><code>fabricops_kit.pipeline.shared.resolve_pipeline_data_contract</code></li>
<li><code>fabricops_kit.pipeline.shared.resolve_source_drift_observation_columns</code></li>
<li><code>fabricops_kit.pipeline.shared.select_table_guardrail_rule</code></li>
<li><code>fabricops_kit.pipeline.shared.set_current_source_observation</code></li>
<li><code>fabricops_kit.pipeline.shared.source_observation_run_id</code></li>
<li><code>fabricops_kit.pipeline.shared.validate_grain_parameters</code></li>
</ul>


</details>

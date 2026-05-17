# `drift` module

<div class="api-status-block">
  <span class="api-chip api-chip-module">Module overview</span>
</div>

## Module dependency summary

- **Essential:** 0
- **Optional:** 4
- **Internal:** 14
- **Depends On:** 1 modules
- **Used By:** 0 modules

## Essential callables

| Callable | Type | Summary | Related helpers |
|---|---|---|---|
| — | — | No recommended entrypoints configured. | — |

## Optional callables

| Callable | Type | Summary | Related helpers |
|---|---|---|---|
| [`check_partition_drift`](../../reference/check_partition_drift/) | function | Check partition-level drift using keys, partitions, and optional watermark baselines. | — |
| [`check_profile_drift`](../../reference/check_profile_drift/) | function | Compare profile metrics against a baseline profile and drift thresholds. | — |
| [`check_schema_drift`](../../reference/check_schema_drift/) | function | Compare a current dataframe schema against a baseline schema snapshot. | — |
| [`summarize_drift_results`](../../reference/summarize_drift_results/) | function | Summarize schema, partition, and profile drift outcomes into one decision. | — |

## Related internal helpers

| Helper | Related public callables |
|---|---|
| [`_build_pandas_partition_snapshot`](../../reference/internal/drift/_build_pandas_partition_snapshot/) | — |
| [`_build_pandas_schema_snapshot`](../../reference/internal/drift/_build_pandas_schema_snapshot/) | — |
| [`_build_partition_hash`](../../reference/internal/drift/_build_partition_hash/) | — |
| [`_build_spark_partition_snapshot`](../../reference/internal/drift/_build_spark_partition_snapshot/) | — |
| [`_build_spark_schema_snapshot`](../../reference/internal/drift/_build_spark_schema_snapshot/) | — |
| [`_column_hash`](../../reference/internal/drift/_column_hash/) | — |
| [`_hash`](../../reference/internal/drift/_hash/) | — |
| [`_is_closed_partition`](../../reference/internal/drift/_is_closed_partition/) | — |
| [`_is_missing_table_error`](../../reference/internal/drift/_is_missing_table_error/) | — |
| [`_json_dumps`](../../reference/internal/drift/_json_dumps/) | — |
| [`_resolve_change_behavior`](../../reference/internal/drift/_resolve_change_behavior/) | — |
| [`_safe_spark_collect`](../../reference/internal/drift/_safe_spark_collect/) | — |
| [`_utc_now_iso`](../../reference/internal/drift/_utc_now_iso/) | — |
| [`_write_metadata_rows`](../../reference/internal/drift/_write_metadata_rows/) | — |

## Module internal callable graph

```mermaid
flowchart LR
  detect_dataframe_engine --> UnsupportedDataFrameEngineError
  _build_pandas_schema_snapshot --> _column_hash
  _build_spark_schema_snapshot --> _column_hash
  build_schema_snapshot --> detect_dataframe_engine
  build_schema_snapshot --> _build_pandas_schema_snapshot
  build_schema_snapshot --> _build_spark_schema_snapshot
  compare_schema_snapshots --> default_schema_drift_policy
  compare_schema_snapshots --> _resolve_change_behavior
  compare_schema_snapshots --> _resolve_change_behavior
  compare_schema_snapshots --> _resolve_change_behavior
  compare_schema_snapshots --> _resolve_change_behavior
  compare_schema_snapshots --> _resolve_change_behavior
  assert_no_blocking_schema_drift --> SchemaDriftError
  check_schema_drift --> build_schema_snapshot
  check_schema_drift --> compare_schema_snapshots
  check_schema_drift --> default_schema_drift_policy
  build_and_write_schema_snapshot --> build_schema_snapshot
  build_and_write_schema_snapshot --> _write_metadata_rows
  build_and_write_schema_snapshot --> _json_dumps
  build_and_write_schema_snapshot --> _utc_now_iso
  load_latest_schema_snapshot --> _safe_spark_collect
  load_latest_schema_snapshot --> _safe_spark_collect
  load_latest_schema_snapshot --> _is_missing_table_error
  check_partition_drift --> build_partition_snapshot
  check_partition_drift --> compare_partition_snapshots
  check_partition_drift --> default_incremental_safety_policy
  build_and_write_partition_snapshot --> build_partition_snapshot
  build_and_write_partition_snapshot --> _write_metadata_rows
  build_and_write_partition_snapshot --> _json_dumps
  build_and_write_partition_snapshot --> _json_dumps
  build_and_write_partition_snapshot --> _utc_now_iso
  load_latest_partition_snapshot --> _safe_spark_collect
  load_latest_partition_snapshot --> _safe_spark_collect
  load_latest_partition_snapshot --> _is_missing_table_error
  build_drift_evidence_record --> _json_dumps
  build_drift_evidence_record --> _json_dumps
  build_drift_evidence_record --> _utc_now_iso
  _build_partition_hash --> _hash
  _build_pandas_partition_snapshot --> _hash
  _build_pandas_partition_snapshot --> _build_partition_hash
```

## Cross-module callable graph

```mermaid
flowchart LR
  fabricops_kit_drift__json_dumps --> fabricops_kit__utils__to_jsonable
  fabricops_kit_drift__build_pandas_partition_snapshot --> fabricops_kit__utils__to_jsonable
  fabricops_kit_drift__build_pandas_partition_snapshot --> fabricops_kit__utils__to_jsonable
  fabricops_kit_drift__build_pandas_partition_snapshot --> fabricops_kit__utils__to_jsonable
  fabricops_kit_drift__build_spark_partition_snapshot --> fabricops_kit__utils__to_jsonable
  fabricops_kit_drift__build_spark_partition_snapshot --> fabricops_kit__utils__to_jsonable
  fabricops_kit_drift__build_spark_partition_snapshot --> fabricops_kit__utils__to_jsonable
  fabricops_kit_drift_compare_partition_snapshots --> fabricops_kit__utils__to_jsonable
  fabricops_kit_drift_compare_partition_snapshots --> fabricops_kit__utils__to_jsonable
  fabricops_kit_drift_build_incremental_safety_records --> fabricops_kit__utils__to_jsonable
```

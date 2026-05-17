# `drift` module

<div class="api-status-block">
  <span class="api-chip api-chip-module">Module overview</span>
</div>

## Module dependency summary

<div class="module-table-scroll">
| Callable count | Internal helper count | Outbound references | Inbound references |
|---:|---:|---:|---:|
| 4 | 14 | 1 | 0 |
</div>

## Module purpose

Owns schema/profile/data drift checks as engineering guardrails during pipeline runs.

## Public callables

<div class="module-table-scroll">
| Callable | Tier | Type | Summary | Related helpers |
|---|---|---|---|---|
| [`check_partition_drift`](../../reference/check_partition_drift/) | Optional | function | Check partition-level drift using keys, partitions, and optional watermark baselines. | — |
| [`check_profile_drift`](../../reference/check_profile_drift/) | Optional | function | Compare profile metrics against a baseline profile and drift thresholds. | — |
| [`check_schema_drift`](../../reference/check_schema_drift/) | Optional | function | Compare a current dataframe schema against a baseline schema snapshot. | — |
| [`summarize_drift_results`](../../reference/summarize_drift_results/) | Optional | function | Summarize schema, partition, and profile drift outcomes into one decision. | — |
</div>

## Advanced dependency sections


### Related internal helpers

<details>
<summary>Expand internal helper table</summary>

<div class="module-table-scroll">
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
</div>

</details>

### Module internal callable dependencies

<details>
<summary>Expand module internal callable graph</summary>

<div class="module-mermaid-scroll">
```mermaid
flowchart LR
  n1["drift._build_pandas_partition_snapshot"] --> n1b["drift._build_partition_hash"]
  n2["drift._build_pandas_partition_snapshot"] --> n2b["drift._hash"]
  n3["drift._build_pandas_schema_snapshot"] --> n3b["drift._column_hash"]
  n4["drift._build_partition_hash"] --> n4b["drift._hash"]
  n5["drift._build_spark_partition_snapshot"] --> n5b["drift._build_partition_hash"]
  n6["drift._build_spark_schema_snapshot"] --> n6b["drift._column_hash"]
  n7["drift.build_and_write_partition_snapshot"] --> n7b["drift._json_dumps"]
  n8["drift.build_and_write_partition_snapshot"] --> n8b["drift._utc_now_iso"]
  n9["drift.build_and_write_partition_snapshot"] --> n9b["drift._write_metadata_rows"]
  n10["drift.build_and_write_partition_snapshot"] --> n10b["drift.build_partition_snapshot"]
  n11["drift.build_and_write_schema_snapshot"] --> n11b["drift._json_dumps"]
  n12["drift.build_and_write_schema_snapshot"] --> n12b["drift._utc_now_iso"]
  n13["drift.build_and_write_schema_snapshot"] --> n13b["drift._write_metadata_rows"]
  n14["drift.build_and_write_schema_snapshot"] --> n14b["drift.build_schema_snapshot"]
  n15["drift.build_drift_evidence_record"] --> n15b["drift._json_dumps"]
  n16["drift.build_drift_evidence_record"] --> n16b["drift._utc_now_iso"]
  n17["drift.build_partition_snapshot"] --> n17b["drift._build_pandas_partition_snapshot"]
  n18["drift.build_partition_snapshot"] --> n18b["drift._build_spark_partition_snapshot"]
  n19["drift.build_partition_snapshot"] --> n19b["drift.detect_dataframe_engine"]
  n20["drift.build_schema_snapshot"] --> n20b["drift._build_pandas_schema_snapshot"]
  n21["drift.build_schema_snapshot"] --> n21b["drift._build_spark_schema_snapshot"]
  n22["drift.build_schema_snapshot"] --> n22b["drift.detect_dataframe_engine"]
  n23["drift.check_partition_drift"] --> n23b["drift.build_partition_snapshot"]
  n24["drift.check_partition_drift"] --> n24b["drift.compare_partition_snapshots"]
  n25["drift.check_partition_drift"] --> n25b["drift.default_incremental_safety_policy"]
  n26["drift.check_schema_drift"] --> n26b["drift.build_schema_snapshot"]
  n27["drift.check_schema_drift"] --> n27b["drift.compare_schema_snapshots"]
  n28["drift.check_schema_drift"] --> n28b["drift.default_schema_drift_policy"]
  n29["drift.compare_partition_snapshots"] --> n29b["drift._is_closed_partition"]
  n30["drift.compare_partition_snapshots"] --> n30b["drift.default_incremental_safety_policy"]
  n31["drift.compare_schema_snapshots"] --> n31b["drift._resolve_change_behavior"]
  n32["drift.compare_schema_snapshots"] --> n32b["drift.default_schema_drift_policy"]
  n33["drift.load_latest_partition_snapshot"] --> n33b["drift._is_missing_table_error"]
  n34["drift.load_latest_partition_snapshot"] --> n34b["drift._safe_spark_collect"]
  n35["drift.load_latest_schema_snapshot"] --> n35b["drift._is_missing_table_error"]
  n36["drift.load_latest_schema_snapshot"] --> n36b["drift._safe_spark_collect"]
```
</div>

</details>

### Cross-module references

<div class="module-mermaid-scroll">
```mermaid
flowchart LR
  c1["drift._build_pandas_partition_snapshot"] --> d1["_utils._to_jsonable"]
  c2["drift._build_spark_partition_snapshot"] --> d2["_utils._to_jsonable"]
  c3["drift._json_dumps"] --> d3["_utils._to_jsonable"]
  c4["drift.build_incremental_safety_records"] --> d4["_utils._to_jsonable"]
  c5["drift.compare_partition_snapshots"] --> d5["_utils._to_jsonable"]
```
</div>

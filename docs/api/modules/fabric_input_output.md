# `fabric_input_output` module

<div class="api-status-block">
  <span class="api-chip api-chip-module">Module overview</span>
</div>

## Module dependency summary

<div class="module-table-scroll">
| Callable count | Internal helper count | Outbound references | Inbound references |
|---:|---:|---:|---:|
| 8 | 3 | 1 | 2 |
</div>

## Module purpose

Owns Fabric read/write helpers for Lakehouse, Warehouse, and file/table IO.

## Public callables

<div class="module-table-scroll">
| Callable | Tier | Type | Summary | Related helpers |
|---|---|---|---|---|
| [`read_lakehouse_table`](../../reference/read_lakehouse_table/) | Essential | function | Read a Delta table from a Fabric lakehouse. | [`_get_spark`](../../reference/internal/fabric_input_output/_get_spark/) (internal) |
| [`read_warehouse_table`](../../reference/read_warehouse_table/) | Essential | function | Read a table from a Microsoft Fabric warehouse. | [`_get_spark`](../../reference/internal/fabric_input_output/_get_spark/) (internal) |
| [`write_lakehouse_table`](../../reference/write_lakehouse_table/) | Essential | function | Write a Spark DataFrame to a Fabric lakehouse Delta table. | — |
| [`write_warehouse_table`](../../reference/write_warehouse_table/) | Essential | function | Write a Spark DataFrame to a Microsoft Fabric warehouse table. | — |
| [`read_lakehouse_csv`](../../reference/read_lakehouse_csv/) | Optional | function | Read a CSV file from a Fabric lakehouse Files path. | [`_get_spark`](../../reference/internal/fabric_input_output/_get_spark/) (internal) |
| [`read_lakehouse_excel`](../../reference/read_lakehouse_excel/) | Optional | function | Read an Excel file from a Fabric lakehouse Files path. | [`_get_spark`](../../reference/internal/fabric_input_output/_get_spark/) (internal) |
| [`read_lakehouse_parquet`](../../reference/read_lakehouse_parquet/) | Optional | function | Read a Parquet file from a Fabric lakehouse Files path. | [`_convert_single_parquet_ns_to_us`](../../reference/internal/fabric_input_output/_convert_single_parquet_ns_to_us/) (internal), [`_get_spark`](../../reference/internal/fabric_input_output/_get_spark/) (internal) |
</div>

## Advanced dependency sections


### Related internal helpers

<div class="module-table-scroll">
| Helper | Related public callables |
|---|---|
| [`_convert_single_parquet_ns_to_us`](../../reference/internal/fabric_input_output/_convert_single_parquet_ns_to_us/) | [`read_lakehouse_parquet`](../../reference/read_lakehouse_parquet/) |
| [`_get_fabric_runtime_context`](../../reference/internal/fabric_input_output/_get_fabric_runtime_context/) | — |
| [`_get_spark`](../../reference/internal/fabric_input_output/_get_spark/) | [`read_lakehouse_csv`](../../reference/read_lakehouse_csv/), [`read_lakehouse_excel`](../../reference/read_lakehouse_excel/), [`read_lakehouse_parquet`](../../reference/read_lakehouse_parquet/), [`read_lakehouse_table`](../../reference/read_lakehouse_table/), [`read_warehouse_table`](../../reference/read_warehouse_table/) |
</div>

### Module internal callable dependencies

<details>
<summary>Expand module internal callable graph</summary>

<div class="module-mermaid-scroll">
```mermaid
flowchart LR
  n1["fabric_input_output.check_naming_convention"] --> n1b["fabric_input_output._get_fabric_runtime_context"]
  n2["fabric_input_output.read_lakehouse_csv"] --> n2b["fabric_input_output._get_spark"]
  n3["fabric_input_output.read_lakehouse_excel"] --> n3b["fabric_input_output._get_spark"]
  n4["fabric_input_output.read_lakehouse_parquet"] --> n4b["fabric_input_output._convert_single_parquet_ns_to_us"]
  n5["fabric_input_output.read_lakehouse_parquet"] --> n5b["fabric_input_output._get_spark"]
  n6["fabric_input_output.read_lakehouse_table"] --> n6b["fabric_input_output._get_spark"]
  n7["fabric_input_output.read_warehouse_table"] --> n7b["fabric_input_output._get_spark"]
  n8["fabric_input_output.seed_minimal_sample_source_table"] --> n8b["fabric_input_output._get_spark"]
  n9["fabric_input_output.seed_minimal_sample_source_table"] --> n9b["fabric_input_output.write_lakehouse_table"]
```
</div>

</details>

### Cross-module references

<div class="module-mermaid-scroll">
```mermaid
flowchart LR
  c1["fabric_input_output.load_config"] --> d1["config.load_config"]
  c2["fabric_input_output.read_lakehouse_csv"] --> d2["config._get_store"]
  c3["fabric_input_output.read_lakehouse_excel"] --> d3["config._get_store"]
  c4["fabric_input_output.read_lakehouse_parquet"] --> d4["config._get_store"]
  c5["fabric_input_output.read_lakehouse_table"] --> d5["config._get_store"]
  c6["fabric_input_output.read_warehouse_table"] --> d6["config._get_store"]
  c7["fabric_input_output.write_lakehouse_table"] --> d7["config._get_store"]
  c8["fabric_input_output.write_warehouse_table"] --> d8["config._get_store"]
```
</div>

# `fabric_input_output` module

<div class="api-status-block">
  <span class="api-chip api-chip-module">Module overview</span>
</div>

## Module dependency summary

<div class="module-summary-cards"><span class="reference-chip">Callable count: 8</span><span class="reference-chip">Outbound: 1</span><span class="reference-chip">Inbound: 2</span></div>

## Module purpose

Owns Fabric read/write helpers for Lakehouse, Warehouse, and file/table IO.

## Public callables

<div class="module-table-scroll">
<table>
  <thead>
    <tr>
      <th>Callable</th>
      <th>Tier</th>
      <th>Type</th>
      <th>Summary</th>
      <th>Related helpers</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><a href="../../reference/read_lakehouse_table/"><code>read_lakehouse_table</code></a></td>
      <td>Essential</td>
      <td>function</td>
      <td>Read a Delta table from a Fabric lakehouse.</td>
      <td><a href="../../reference/internal/fabric_input_output/_get_spark/"><code>_get_spark</code></a> (internal)</td>
    </tr>
    <tr>
      <td><a href="../../reference/read_warehouse_table/"><code>read_warehouse_table</code></a></td>
      <td>Essential</td>
      <td>function</td>
      <td>Read a table from a Microsoft Fabric warehouse.</td>
      <td><a href="../../reference/internal/fabric_input_output/_get_spark/"><code>_get_spark</code></a> (internal)</td>
    </tr>
    <tr>
      <td><a href="../../reference/write_lakehouse_table/"><code>write_lakehouse_table</code></a></td>
      <td>Essential</td>
      <td>function</td>
      <td>Write a Spark DataFrame to a Fabric lakehouse Delta table.</td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/write_warehouse_table/"><code>write_warehouse_table</code></a></td>
      <td>Essential</td>
      <td>function</td>
      <td>Write a Spark DataFrame to a Microsoft Fabric warehouse table.</td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/read_lakehouse_csv/"><code>read_lakehouse_csv</code></a></td>
      <td>Optional</td>
      <td>function</td>
      <td>Read a CSV file from a Fabric lakehouse Files path.</td>
      <td><a href="../../reference/internal/fabric_input_output/_get_spark/"><code>_get_spark</code></a> (internal)</td>
    </tr>
    <tr>
      <td><a href="../../reference/read_lakehouse_excel/"><code>read_lakehouse_excel</code></a></td>
      <td>Optional</td>
      <td>function</td>
      <td>Read an Excel file from a Fabric lakehouse Files path.</td>
      <td><a href="../../reference/internal/fabric_input_output/_get_spark/"><code>_get_spark</code></a> (internal)</td>
    </tr>
    <tr>
      <td><a href="../../reference/read_lakehouse_parquet/"><code>read_lakehouse_parquet</code></a></td>
      <td>Optional</td>
      <td>function</td>
      <td>Read a Parquet file from a Fabric lakehouse Files path.</td>
      <td><a href="../../reference/internal/fabric_input_output/_convert_single_parquet_ns_to_us/"><code>_convert_single_parquet_ns_to_us</code></a> (internal), <a href="../../reference/internal/fabric_input_output/_get_spark/"><code>_get_spark</code></a> (internal)</td>
    </tr>
  </tbody>
</table>
</div>

## Advanced dependency sections


### Related internal helpers

<div class="module-table-scroll">
<table>
  <thead>
    <tr>
      <th>Helper</th>
      <th>Related public callables</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><a href="../../reference/internal/fabric_input_output/_convert_single_parquet_ns_to_us/"><code>_convert_single_parquet_ns_to_us</code></a></td>
      <td><a href="../../reference/read_lakehouse_parquet/"><code>read_lakehouse_parquet</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/fabric_input_output/_get_fabric_runtime_context/"><code>_get_fabric_runtime_context</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/fabric_input_output/_get_spark/"><code>_get_spark</code></a></td>
      <td><a href="../../reference/read_lakehouse_csv/"><code>read_lakehouse_csv</code></a>, <a href="../../reference/read_lakehouse_excel/"><code>read_lakehouse_excel</code></a>, <a href="../../reference/read_lakehouse_parquet/"><code>read_lakehouse_parquet</code></a>, <a href="../../reference/read_lakehouse_table/"><code>read_lakehouse_table</code></a>, <a href="../../reference/read_warehouse_table/"><code>read_warehouse_table</code></a></td>
    </tr>
  </tbody>
</table>
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

### Outbound

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

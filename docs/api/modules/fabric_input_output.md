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

### Inside this module, used by, and uses

<div class="module-mermaid-scroll module-diagram-desktop">
```mermaid
flowchart LR
  classDef currentModule fill:#fff3e0,stroke:#ef6c00,stroke-width:3px,color:#3e2723;
  classDef externalModule fill:#f5f5f5,stroke:#9e9e9e,stroke-width:1px,color:#616161;
  classDef currentCallable fill:#ffe0b2,stroke:#ef6c00,stroke-width:2px;
  classDef externalCallable fill:#eceff1,stroke:#90a4ae,stroke-width:1px;
  subgraph m_config[config]
    fabricops_kit_config__get_store["_get_store"]
    fabricops_kit_config_load_config["load_config"]
  end
  subgraph m_data_quality[data_quality]
    fabricops_kit_data_quality_write_dq_rules["write_dq_rules"]
  end
  subgraph m_fabric_input_output[fabric_input_output]
    fabricops_kit_fabric_input_output__convert_single_parquet_ns_to_us["_convert_single_parquet_ns_to_us"]
    fabricops_kit_fabric_input_output__get_fabric_runtime_context["_get_fabric_runtime_context"]
    fabricops_kit_fabric_input_output__get_spark["_get_spark"]
    fabricops_kit_fabric_input_output_check_naming_convention["check_naming_convention"]
    fabricops_kit_fabric_input_output_load_config["load_config"]
    fabricops_kit_fabric_input_output_read_lakehouse_csv["read_lakehouse_csv"]
    fabricops_kit_fabric_input_output_read_lakehouse_excel["read_lakehouse_excel"]
    fabricops_kit_fabric_input_output_read_lakehouse_parquet["read_lakehouse_parquet"]
    fabricops_kit_fabric_input_output_read_lakehouse_table["read_lakehouse_table"]
    fabricops_kit_fabric_input_output_read_warehouse_table["read_warehouse_table"]
    fabricops_kit_fabric_input_output_seed_minimal_sample_source_table["seed_minimal_sample_source_table"]
    fabricops_kit_fabric_input_output_write_lakehouse_table["write_lakehouse_table"]
    fabricops_kit_fabric_input_output_write_warehouse_table["write_warehouse_table"]
  end
  subgraph m_metadata[metadata]
    fabricops_kit_metadata_write_metadata_rows["write_metadata_rows"]
  end
  fabricops_kit_data_quality_write_dq_rules --> fabricops_kit_fabric_input_output_write_lakehouse_table
  fabricops_kit_fabric_input_output_check_naming_convention --> fabricops_kit_fabric_input_output__get_fabric_runtime_context
  fabricops_kit_fabric_input_output_load_config --> fabricops_kit_config_load_config
  fabricops_kit_fabric_input_output_read_lakehouse_csv --> fabricops_kit_config__get_store
  fabricops_kit_fabric_input_output_read_lakehouse_csv --> fabricops_kit_fabric_input_output__get_spark
  fabricops_kit_fabric_input_output_read_lakehouse_excel --> fabricops_kit_config__get_store
  fabricops_kit_fabric_input_output_read_lakehouse_excel --> fabricops_kit_fabric_input_output__get_spark
  fabricops_kit_fabric_input_output_read_lakehouse_parquet --> fabricops_kit_config__get_store
  fabricops_kit_fabric_input_output_read_lakehouse_parquet --> fabricops_kit_fabric_input_output__convert_single_parquet_ns_to_us
  fabricops_kit_fabric_input_output_read_lakehouse_parquet --> fabricops_kit_fabric_input_output__get_spark
  fabricops_kit_fabric_input_output_read_lakehouse_table --> fabricops_kit_config__get_store
  fabricops_kit_fabric_input_output_read_lakehouse_table --> fabricops_kit_fabric_input_output__get_spark
  fabricops_kit_fabric_input_output_read_warehouse_table --> fabricops_kit_config__get_store
  fabricops_kit_fabric_input_output_read_warehouse_table --> fabricops_kit_fabric_input_output__get_spark
  fabricops_kit_fabric_input_output_seed_minimal_sample_source_table --> fabricops_kit_fabric_input_output__get_spark
  fabricops_kit_fabric_input_output_seed_minimal_sample_source_table --> fabricops_kit_fabric_input_output_write_lakehouse_table
  fabricops_kit_fabric_input_output_write_lakehouse_table --> fabricops_kit_config__get_store
  fabricops_kit_fabric_input_output_write_warehouse_table --> fabricops_kit_config__get_store
  fabricops_kit_metadata_write_metadata_rows --> fabricops_kit_fabric_input_output_write_lakehouse_table
  class m_fabric_input_output currentModule;
  class fabricops_kit_fabric_input_output__convert_single_parquet_ns_to_us,fabricops_kit_fabric_input_output__get_fabric_runtime_context,fabricops_kit_fabric_input_output__get_spark,fabricops_kit_fabric_input_output_check_naming_convention,fabricops_kit_fabric_input_output_load_config,fabricops_kit_fabric_input_output_read_lakehouse_csv,fabricops_kit_fabric_input_output_read_lakehouse_excel,fabricops_kit_fabric_input_output_read_lakehouse_parquet,fabricops_kit_fabric_input_output_read_lakehouse_table,fabricops_kit_fabric_input_output_read_warehouse_table,fabricops_kit_fabric_input_output_seed_minimal_sample_source_table,fabricops_kit_fabric_input_output_write_lakehouse_table,fabricops_kit_fabric_input_output_write_warehouse_table currentCallable;
  class fabricops_kit_config__get_store,fabricops_kit_config_load_config,fabricops_kit_data_quality_write_dq_rules,fabricops_kit_metadata_write_metadata_rows externalCallable;
```
</div>

<div class="module-relationship-list module-diagram-mobile">
#### Inside this module

<div class="callable-chip-group">
<a class="reference-chip" href="../modules/fabric_input_output/#check_naming_convention"><code>check_naming_convention</code></a> → <a class="reference-chip" href="../modules/fabric_input_output/#_get_fabric_runtime_context"><code>_get_fabric_runtime_context</code></a>
<a class="reference-chip" href="../../reference/read_lakehouse_csv/"><code>read_lakehouse_csv</code></a> → <a class="reference-chip" href="../modules/fabric_input_output/#_get_spark"><code>_get_spark</code></a>
<a class="reference-chip" href="../../reference/read_lakehouse_excel/"><code>read_lakehouse_excel</code></a> → <a class="reference-chip" href="../modules/fabric_input_output/#_get_spark"><code>_get_spark</code></a>
<a class="reference-chip" href="../../reference/read_lakehouse_parquet/"><code>read_lakehouse_parquet</code></a> → <a class="reference-chip" href="../modules/fabric_input_output/#_convert_single_parquet_ns_to_us"><code>_convert_single_parquet_ns_to_us</code></a>
<a class="reference-chip" href="../../reference/read_lakehouse_parquet/"><code>read_lakehouse_parquet</code></a> → <a class="reference-chip" href="../modules/fabric_input_output/#_get_spark"><code>_get_spark</code></a>
<a class="reference-chip" href="../../reference/read_lakehouse_table/"><code>read_lakehouse_table</code></a> → <a class="reference-chip" href="../modules/fabric_input_output/#_get_spark"><code>_get_spark</code></a>
<a class="reference-chip" href="../../reference/read_warehouse_table/"><code>read_warehouse_table</code></a> → <a class="reference-chip" href="../modules/fabric_input_output/#_get_spark"><code>_get_spark</code></a>
<a class="reference-chip" href="../modules/fabric_input_output/#seed_minimal_sample_source_table"><code>seed_minimal_sample_source_table</code></a> → <a class="reference-chip" href="../modules/fabric_input_output/#_get_spark"><code>_get_spark</code></a>
<a class="reference-chip" href="../modules/fabric_input_output/#seed_minimal_sample_source_table"><code>seed_minimal_sample_source_table</code></a> → <a class="reference-chip" href="../../reference/write_lakehouse_table/"><code>write_lakehouse_table</code></a>
</div>
#### Used by

<div class="callable-chip-group">
<a class="reference-chip" href="../../reference/write_dq_rules/"><code>write_dq_rules</code></a> → <a class="reference-chip" href="../../reference/write_lakehouse_table/"><code>write_lakehouse_table</code></a>
<a class="reference-chip" href="../modules/metadata/#write_metadata_rows"><code>write_metadata_rows</code></a> → <a class="reference-chip" href="../../reference/write_lakehouse_table/"><code>write_lakehouse_table</code></a>
</div>
#### Uses

<div class="callable-chip-group">
<a class="reference-chip" href="../../reference/load_config/"><code>load_config</code></a> → <a class="reference-chip" href="../../reference/load_config/"><code>load_config</code></a>
<a class="reference-chip" href="../../reference/read_lakehouse_csv/"><code>read_lakehouse_csv</code></a> → <a class="reference-chip" href="../modules/config/#_get_store"><code>_get_store</code></a>
<a class="reference-chip" href="../../reference/read_lakehouse_excel/"><code>read_lakehouse_excel</code></a> → <a class="reference-chip" href="../modules/config/#_get_store"><code>_get_store</code></a>
<a class="reference-chip" href="../../reference/read_lakehouse_parquet/"><code>read_lakehouse_parquet</code></a> → <a class="reference-chip" href="../modules/config/#_get_store"><code>_get_store</code></a>
<a class="reference-chip" href="../../reference/read_lakehouse_table/"><code>read_lakehouse_table</code></a> → <a class="reference-chip" href="../modules/config/#_get_store"><code>_get_store</code></a>
<a class="reference-chip" href="../../reference/read_warehouse_table/"><code>read_warehouse_table</code></a> → <a class="reference-chip" href="../modules/config/#_get_store"><code>_get_store</code></a>
<a class="reference-chip" href="../../reference/write_lakehouse_table/"><code>write_lakehouse_table</code></a> → <a class="reference-chip" href="../modules/config/#_get_store"><code>_get_store</code></a>
<a class="reference-chip" href="../../reference/write_warehouse_table/"><code>write_warehouse_table</code></a> → <a class="reference-chip" href="../modules/config/#_get_store"><code>_get_store</code></a>
</div>
</div>

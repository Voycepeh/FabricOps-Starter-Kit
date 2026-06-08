# `fabric_input_output` module

<div class="api-status-block">
  <span class="api-chip api-chip-module">Module overview</span>
</div>

Implementation modules document source-level behavior and internal helper relationships for maintainers. They support debugging and implementation traceability, but they are not the public v1 callable API.

The public v1 callable API is controlled by `src/fabricops_kit/__init__.py::__all__` and is browsed from the Function Reference catalogue.

## Module overview badges

<div class="module-summary-cards"><span class="reference-chip">Callable count: 7</span><span class="reference-chip">Internal helpers: 3</span><span class="reference-chip">Outbound: 1</span><span class="reference-chip">Inbound: 4</span></div>

## Module purpose

Owns Fabric read/write helpers for Lakehouse, Warehouse, and file/table IO.

## Module manifest

<table>
  <thead>
    <tr>
      <th>Field</th>
      <th>Value</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Module name</td>
      <td><code>fabric_input_output</code></td>
    </tr>
    <tr>
      <td>Module purpose</td>
      <td>Owns Fabric read/write helpers for Lakehouse, Warehouse, and file/table IO.</td>
    </tr>
    <tr>
      <td>Public callable count</td>
      <td>7</td>
    </tr>
    <tr>
      <td>Internal helper count</td>
      <td>3</td>
    </tr>
    <tr>
      <td>Inbound module count</td>
      <td>4</td>
    </tr>
    <tr>
      <td>Outbound module count</td>
      <td>1</td>
    </tr>
    <tr>
      <td>External callers</td>
      <td><code>data_agreement</code>, <code>governance_review</code>, <code>metadata</code>, <code>pipeline</code></td>
    </tr>
    <tr>
      <td>External callees</td>
      <td><code>config</code></td>
    </tr>
  </tbody>
</table>

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
      <td><a href="../../reference/read_lakehouse_csv/"><code>read_lakehouse_csv</code></a></td>
      <td>Callable</td>
      <td>function</td>
      <td>Read a CSV file from a configured Fabric lakehouse Files path.</td>
      <td><a href="../../reference/internal/fabric_input_output/_get_spark/"><code>_get_spark</code></a> (internal), <a href="../../reference/internal/fabric_input_output/_lakehouse_file_path/"><code>_lakehouse_file_path</code></a> (internal)</td>
    </tr>
    <tr>
      <td><a href="../../reference/read_lakehouse_excel/"><code>read_lakehouse_excel</code></a></td>
      <td>Callable</td>
      <td>function</td>
      <td>Read an Excel file from a configured Fabric lakehouse Files path.</td>
      <td><a href="../../reference/internal/fabric_input_output/_get_spark/"><code>_get_spark</code></a> (internal), <a href="../../reference/internal/fabric_input_output/_lakehouse_file_path/"><code>_lakehouse_file_path</code></a> (internal)</td>
    </tr>
    <tr>
      <td><a href="../../reference/read_lakehouse_parquet/"><code>read_lakehouse_parquet</code></a></td>
      <td>Callable</td>
      <td>function</td>
      <td>Read a Parquet path from a configured Fabric lakehouse Files path.</td>
      <td><a href="../../reference/internal/fabric_input_output/_convert_single_parquet_ns_to_us/"><code>_convert_single_parquet_ns_to_us</code></a> (internal), <a href="../../reference/internal/fabric_input_output/_get_spark/"><code>_get_spark</code></a> (internal), <a href="../../reference/internal/fabric_input_output/_lakehouse_file_path/"><code>_lakehouse_file_path</code></a> (internal)</td>
    </tr>
    <tr>
      <td><a href="../../reference/read_lakehouse_table/"><code>read_lakehouse_table</code></a></td>
      <td>Callable</td>
      <td>function</td>
      <td>Read a table from a configured Fabric lakehouse target.</td>
      <td><a href="../../reference/internal/fabric_input_output/_get_spark/"><code>_get_spark</code></a> (internal)</td>
    </tr>
    <tr>
      <td><a href="../../reference/read_warehouse_table/"><code>read_warehouse_table</code></a></td>
      <td>Callable</td>
      <td>function</td>
      <td>Read a table from a configured Fabric warehouse target.</td>
      <td><a href="../../reference/internal/fabric_input_output/_get_spark/"><code>_get_spark</code></a> (internal)</td>
    </tr>
    <tr>
      <td><a href="../../reference/write_lakehouse_table/"><code>write_lakehouse_table</code></a></td>
      <td>Callable</td>
      <td>function</td>
      <td>Write a DataFrame to a configured Fabric lakehouse target.</td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/write_warehouse_table/"><code>write_warehouse_table</code></a></td>
      <td>Callable</td>
      <td>function</td>
      <td>Write a DataFrame to a configured Fabric warehouse target.</td>
      <td>—</td>
    </tr>
  </tbody>
</table>
</div>

## Module relationships


### Callable relationships


#### Inside this module

<section class="callable-relationship-card">
<h5>fabric_input_output</h5>
<h6>Public callables</h6>
<ul class="callable-relationship-rows">
<li>
<a class="reference-chip" href="../../reference/read_lakehouse_csv/"><code>read_lakehouse_csv</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_get_spark"><code>_get_spark</code></a>, <a class="reference-chip" href="#_lakehouse_file_path"><code>_lakehouse_file_path</code></a>
</li>
<li>
<a class="reference-chip" href="../../reference/read_lakehouse_excel/"><code>read_lakehouse_excel</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_get_spark"><code>_get_spark</code></a>, <a class="reference-chip" href="#_lakehouse_file_path"><code>_lakehouse_file_path</code></a>
</li>
<li>
<a class="reference-chip" href="../../reference/read_lakehouse_parquet/"><code>read_lakehouse_parquet</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_convert_single_parquet_ns_to_us"><code>_convert_single_parquet_ns_to_us</code></a>, <a class="reference-chip" href="#_get_spark"><code>_get_spark</code></a>, <a class="reference-chip" href="#_lakehouse_file_path"><code>_lakehouse_file_path</code></a>
</li>
<li>
<a class="reference-chip" href="../../reference/read_lakehouse_table/"><code>read_lakehouse_table</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_get_spark"><code>_get_spark</code></a>
</li>
<li>
<a class="reference-chip" href="../../reference/read_warehouse_table/"><code>read_warehouse_table</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_get_spark"><code>_get_spark</code></a>
</li>
<li>
<a class="reference-chip" href="../../reference/write_lakehouse_table/"><code>write_lakehouse_table</code></a>
 <span class="callable-relationship-uses">uses:</span>
<span>None.</span>
</li>
<li>
<a class="reference-chip" href="../../reference/write_warehouse_table/"><code>write_warehouse_table</code></a>
 <span class="callable-relationship-uses">uses:</span>
<span>None.</span>
</li>
</ul>
</section>

### Related internal helpers

<details>
<summary>Show internal helpers</summary>

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
      <td><a href="../../reference/internal/fabric_input_output/_get_spark/"><code>_get_spark</code></a></td>
      <td><a href="../../reference/read_lakehouse_csv/"><code>read_lakehouse_csv</code></a>, <a href="../../reference/read_lakehouse_excel/"><code>read_lakehouse_excel</code></a>, <a href="../../reference/read_lakehouse_parquet/"><code>read_lakehouse_parquet</code></a>, <a href="../../reference/read_lakehouse_table/"><code>read_lakehouse_table</code></a>, <a href="../../reference/read_warehouse_table/"><code>read_warehouse_table</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/fabric_input_output/_lakehouse_file_path/"><code>_lakehouse_file_path</code></a></td>
      <td><a href="../../reference/read_lakehouse_csv/"><code>read_lakehouse_csv</code></a>, <a href="../../reference/read_lakehouse_excel/"><code>read_lakehouse_excel</code></a>, <a href="../../reference/read_lakehouse_parquet/"><code>read_lakehouse_parquet</code></a></td>
    </tr>
  </tbody>
</table>
</div>

<h6>Internal helpers details</h6>
<ul class="callable-relationship-rows">
<li>
<a class="reference-chip" href="#_convert_single_parquet_ns_to_us"><code>_convert_single_parquet_ns_to_us</code></a>
</li>
<li>
<a class="reference-chip" href="#_get_spark"><code>_get_spark</code></a>
</li>
<li>
<a class="reference-chip" href="#_lakehouse_file_path"><code>_lakehouse_file_path</code></a>
</li>
</ul>
</details>

### External callers

**data_agreement**
<a class="reference-chip" href="../data_agreement/#_ensure_metadata_tables"><code>_ensure_metadata_tables</code></a>, <a class="reference-chip" href="../data_agreement/#_list_all_data_agreement_rows"><code>_list_all_data_agreement_rows</code></a>, <a class="reference-chip" href="../data_agreement/#_list_data_stewards"><code>_list_data_stewards</code></a>, <a class="reference-chip" href="../data_agreement/#_write_row"><code>_write_row</code></a>

**governance_review**
<a class="reference-chip" href="../governance_review/#_setup_governance_metadata_tables"><code>_setup_governance_metadata_tables</code></a>, <a class="reference-chip" href="../../reference/enforce_dq_rules/"><code>enforce_dq_rules</code></a>, <a class="reference-chip" href="../../reference/load_catalogue_profile_rows/"><code>load_catalogue_profile_rows</code></a>, <a class="reference-chip" href="../../reference/record_table_governance/"><code>record_table_governance</code></a>, <a class="reference-chip" href="../../reference/widget_select_catalogue_table/"><code>widget_select_catalogue_table</code></a>

**metadata**
<a class="reference-chip" href="../metadata/#_load_notebook_registry"><code>_load_notebook_registry</code></a>, <a class="reference-chip" href="../metadata/#_register_current_notebook"><code>_register_current_notebook</code></a>, <a class="reference-chip" href="../metadata/#_setup_notebook_registry_table"><code>_setup_notebook_registry_table</code></a>

**pipeline**
<a class="reference-chip" href="../../reference/write_catalogue_evidence/"><code>write_catalogue_evidence</code></a>, <a class="reference-chip" href="../../reference/write_pipeline_lineage/"><code>write_pipeline_lineage</code></a>, <a class="reference-chip" href="../../reference/write_pipeline_run_summary/"><code>write_pipeline_run_summary</code></a>

### External callees

**config**
<a class="reference-chip" href="../config/#_get_store"><code>_get_store</code></a>

# `fabric_input_output` module

<div class="api-status-block">
  <span class="api-chip api-chip-module">Module overview</span>
</div>

Implementation modules document source-level behavior and internal helper relationships for maintainers. They support debugging and implementation traceability, but they are not the public v1 callable API.

The public v1 callable API is controlled by `src/fabricops_kit/__init__.py::__all__` and is browsed from the Function Reference catalogue.

## Module overview badges

<div class="module-summary-cards"><span class="reference-chip">Callable count: 2</span><span class="reference-chip">Internal helpers: 12</span><span class="reference-chip">Uses 1 external module</span><span class="reference-chip">Used by 6 external modules</span></div>

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
      <td>2</td>
    </tr>
    <tr>
      <td>Internal helper count</td>
      <td>12</td>
    </tr>
    <tr>
      <td>Used by external module count</td>
      <td>6</td>
    </tr>
    <tr>
      <td>Uses external module count</td>
      <td>1</td>
    </tr>
    <tr>
      <td>External modules using this module</td>
      <td><code>config</code>, <code>data_agreement</code>, <code>governance_review</code>, <code>guardrails</code>, <code>metadata</code>, <code>pipeline</code></td>
    </tr>
    <tr>
      <td>External modules this module uses</td>
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
      <td><a href="../reference/read_data/"><code>read_data</code></a></td>
      <td>Callable</td>
      <td>function</td>
      <td>Read Lakehouse tables, Lakehouse files, or Warehouse tables through one notebook-facing IO function.</td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../reference/write_data/"><code>write_data</code></a></td>
      <td>Callable</td>
      <td>function</td>
      <td>Write Lakehouse or Warehouse targets through one notebook-facing IO function.</td>
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
<a class="reference-chip" href="../reference/read_data/"><code>read_data</code></a>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>read_lakehouse_csv</code></span>, <span class="reference-chip"><code>read_lakehouse_excel</code></span>, <span class="reference-chip"><code>read_lakehouse_parquet</code></span>, <span class="reference-chip"><code>read_lakehouse_table</code></span>, <span class="reference-chip"><code>read_warehouse_table</code></span>
</li>
<li>
<a class="reference-chip" href="../reference/write_data/"><code>write_data</code></a>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>write_lakehouse_table</code></span>, <span class="reference-chip"><code>write_warehouse_table</code></span>
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
      <td><code>_PandasProxy.__getattr__</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_configured_lakehouse_schema</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_convert_single_parquet_ns_to_us</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_get_spark</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_lakehouse_file_path</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_normalize_schema_name</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_normalize_table_name</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_qualified_table_name</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_resolve_lakehouse_schema</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_resolve_lakehouse_table_identifier</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_resolve_lakehouse_table_path</code></td>
      <td>—</td>
    </tr>
  </tbody>
</table>
</div>

<h6>Internal helpers details</h6>
<ul class="callable-relationship-rows">
<li>
<span class="reference-chip"><code>_PandasProxy.__getattr__</code></span>
</li>
<li>
<span class="reference-chip"><code>_configured_lakehouse_schema</code></span>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_normalize_schema_name</code></span>
</li>
<li>
<span class="reference-chip"><code>_convert_single_parquet_ns_to_us</code></span>
</li>
<li>
<span class="reference-chip"><code>_get_spark</code></span>
</li>
<li>
<span class="reference-chip"><code>_lakehouse_file_path</code></span>
</li>
<li>
<span class="reference-chip"><code>_normalize_schema_name</code></span>
</li>
<li>
<span class="reference-chip"><code>_normalize_table_name</code></span>
</li>
<li>
<span class="reference-chip"><code>_qualified_table_name</code></span>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_normalize_schema_name</code></span>, <span class="reference-chip"><code>_normalize_table_name</code></span>
</li>
<li>
<span class="reference-chip"><code>_resolve_lakehouse_schema</code></span>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_normalize_schema_name</code></span>
</li>
<li>
<span class="reference-chip"><code>_resolve_lakehouse_table_identifier</code></span>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_normalize_table_name</code></span>, <span class="reference-chip"><code>_qualified_table_name</code></span>, <span class="reference-chip"><code>_resolve_lakehouse_schema</code></span>
</li>
<li>
<span class="reference-chip"><code>_resolve_lakehouse_table_path</code></span>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_normalize_table_name</code></span>, <span class="reference-chip"><code>_resolve_lakehouse_schema</code></span>
</li>
</ul>
</details>

### External callers

**config**
<a class="reference-chip" href="config/#_setup_metadata_table_registry"><code>_setup_metadata_table_registry</code></a>, <a class="reference-chip" href="config/#_validate_metadata_table_registration"><code>_validate_metadata_table_registration</code></a>

**data_agreement**
<a class="reference-chip" href="data_agreement/#_list_all_data_agreement_rows"><code>_list_all_data_agreement_rows</code></a>, <a class="reference-chip" href="data_agreement/#_list_data_stewards"><code>_list_data_stewards</code></a>, <a class="reference-chip" href="data_agreement/#_write_row"><code>_write_row</code></a>

**governance_review**
<a class="reference-chip" href="governance_review/#_read_guardrail_rule_metadata"><code>_read_guardrail_rule_metadata</code></a>, <a class="reference-chip" href="governance_review/#_read_metadata_rows"><code>_read_metadata_rows</code></a>, <a class="reference-chip" href="governance_review/#_read_metadata_table_or_empty"><code>_read_metadata_table_or_empty</code></a>, <a class="reference-chip" href="governance_review/#_write_rule_records"><code>_write_rule_records</code></a>, <a class="reference-chip" href="governance_review/#_write_table_metadata_enrichment_records"><code>_write_table_metadata_enrichment_records</code></a>, <a class="reference-chip" href="../reference/get_latest_metadata_catalogue/"><code>get_latest_metadata_catalogue</code></a>, <a class="reference-chip" href="governance_review/#load_catalogue_profile_rows"><code>load_catalogue_profile_rows</code></a>, <a class="reference-chip" href="governance_review/#record_table_governance"><code>record_table_governance</code></a>

**guardrails**
<a class="reference-chip" href="guardrails/#enforce_profile_behavior"><code>enforce_profile_behavior</code></a>

**metadata**
<a class="reference-chip" href="metadata/#_load_notebook_registry"><code>_load_notebook_registry</code></a>, <a class="reference-chip" href="metadata/#_register_current_notebook"><code>_register_current_notebook</code></a>, <a class="reference-chip" href="metadata/#_write_guardrail_result_row"><code>_write_guardrail_result_row</code></a>

**pipeline**
<a class="reference-chip" href="pipeline/#write_catalogue_evidence"><code>write_catalogue_evidence</code></a>, <a class="reference-chip" href="../reference/write_pipeline_lineage/"><code>write_pipeline_lineage</code></a>, <a class="reference-chip" href="../reference/write_pipeline_run_summary/"><code>write_pipeline_run_summary</code></a>

### External callees

**config**
<a class="reference-chip" href="config/#_get_store"><code>_get_store</code></a>, <a class="reference-chip" href="config/#resolve_fabric_context"><code>resolve_fabric_context</code></a>

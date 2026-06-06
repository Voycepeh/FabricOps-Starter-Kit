# `config` module

<div class="api-status-block">
  <span class="api-chip api-chip-module">Module overview</span>
</div>

Implementation modules document source-level behavior and internal helper relationships for maintainers. They support debugging and implementation traceability, but they are not the public v1 callable API.

The public v1 callable API is controlled by `src/fabricops_kit/__init__.py::__all__` and is browsed from the Function Reference catalogue.

## Module overview badges

<div class="module-summary-cards"><span class="reference-chip">Callable count: 2</span><span class="reference-chip">Internal helpers: 17</span><span class="reference-chip">Outbound: 3</span><span class="reference-chip">Inbound: 2</span></div>

## Module purpose

Owns environment setup, runtime initialization, paths, and notebook-wide configuration.

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
      <td><code>config</code></td>
    </tr>
    <tr>
      <td>Module purpose</td>
      <td>Owns environment setup, runtime initialization, paths, and notebook-wide configuration.</td>
    </tr>
    <tr>
      <td>Public callable count</td>
      <td>2</td>
    </tr>
    <tr>
      <td>Internal helper count</td>
      <td>17</td>
    </tr>
    <tr>
      <td>Inbound module count</td>
      <td>2</td>
    </tr>
    <tr>
      <td>Outbound module count</td>
      <td>3</td>
    </tr>
    <tr>
      <td>External callers</td>
      <td><code>data_agreement</code>, <code>fabric_input_output</code></td>
    </tr>
    <tr>
      <td>External callees</td>
      <td><code>data_agreement</code>, <code>governance_review</code>, <code>metadata</code></td>
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
      <td><a href="../../reference/setup_metadata_tables/"><code>setup_metadata_tables</code></a></td>
      <td>Callable</td>
      <td>function</td>
      <td>Create or validate all FabricOps metadata tables through one setup action.</td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/setup_notebook/"><code>setup_notebook</code></a></td>
      <td>Callable</td>
      <td>function</td>
      <td>Shared environment setup and runtime validation for notebook templates.</td>
      <td><a href="../../reference/internal/config/_get_store/"><code>_get_store</code></a> (internal), <a href="../../reference/internal/config/_run_config_smoke_tests/"><code>_run_config_smoke_tests</code></a> (internal), <a href="../../reference/internal/config/_validate_framework_config/"><code>_validate_framework_config</code></a> (internal)</td>
    </tr>
  </tbody>
</table>
</div>

## Module relationships


### Callable relationships


#### Inside this module

<section class="callable-relationship-card">
<h5>config</h5>
<h6>Public callables</h6>
<ul class="callable-relationship-rows">
<li>
<a class="reference-chip" href="../../reference/setup_metadata_tables/"><code>setup_metadata_tables</code></a>
 <span class="callable-relationship-uses">uses:</span>
<span>None.</span>
</li>
<li>
<a class="reference-chip" href="../../reference/setup_notebook/"><code>setup_notebook</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_get_store"><code>_get_store</code></a>, <a class="reference-chip" href="#_run_config_smoke_tests"><code>_run_config_smoke_tests</code></a>, <a class="reference-chip" href="#_validate_framework_config"><code>_validate_framework_config</code></a>
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
      <td><a href="../../reference/internal/config/_assert_valid_dataset_contract/"><code>_assert_valid_dataset_contract</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/config/_bootstrap_fabric_env/"><code>_bootstrap_fabric_env</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/config/_check_fabric_ai_functions_available/"><code>_check_fabric_ai_functions_available</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/config/_check_spark_session/"><code>_check_spark_session</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/config/_configure_fabric_ai_functions/"><code>_configure_fabric_ai_functions</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/config/_default_schema_text/"><code>_default_schema_text</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/config/_format_error_path/"><code>_format_error_path</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/config/_get_fabric_runtime_metadata/"><code>_get_fabric_runtime_metadata</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/config/_get_store/"><code>_get_store</code></a></td>
      <td><a href="../../reference/setup_notebook/"><code>setup_notebook</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/config/_load_and_validate_dataset_contract/"><code>_load_and_validate_dataset_contract</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/config/_load_dataset_contract/"><code>_load_dataset_contract</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/config/_load_schema/"><code>_load_schema</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/config/_normalize_name/"><code>_normalize_name</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/config/_run_config_smoke_tests/"><code>_run_config_smoke_tests</code></a></td>
      <td><a href="../../reference/setup_notebook/"><code>setup_notebook</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/config/_validate_dataset_contract/"><code>_validate_dataset_contract</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/config/_validate_framework_config/"><code>_validate_framework_config</code></a></td>
      <td><a href="../../reference/setup_notebook/"><code>setup_notebook</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/config/_validate_notebook_name/"><code>_validate_notebook_name</code></a></td>
      <td>—</td>
    </tr>
  </tbody>
</table>
</div>

<h6>Internal helpers details</h6>
<ul class="callable-relationship-rows">
<li>
<a class="reference-chip" href="#_assert_valid_dataset_contract"><code>_assert_valid_dataset_contract</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_validate_dataset_contract"><code>_validate_dataset_contract</code></a>
</li>
<li>
<a class="reference-chip" href="#_bootstrap_fabric_env"><code>_bootstrap_fabric_env</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_get_fabric_runtime_metadata"><code>_get_fabric_runtime_metadata</code></a>, <a class="reference-chip" href="#_get_store"><code>_get_store</code></a>, <a class="reference-chip" href="#_run_config_smoke_tests"><code>_run_config_smoke_tests</code></a>, <a class="reference-chip" href="#_validate_framework_config"><code>_validate_framework_config</code></a>
</li>
<li>
<a class="reference-chip" href="#_check_fabric_ai_functions_available"><code>_check_fabric_ai_functions_available</code></a>
</li>
<li>
<a class="reference-chip" href="#_check_spark_session"><code>_check_spark_session</code></a>
</li>
<li>
<a class="reference-chip" href="#_configure_fabric_ai_functions"><code>_configure_fabric_ai_functions</code></a>
</li>
<li>
<a class="reference-chip" href="#_default_schema_text"><code>_default_schema_text</code></a>
</li>
<li>
<a class="reference-chip" href="#_format_error_path"><code>_format_error_path</code></a>
</li>
<li>
<a class="reference-chip" href="#_get_fabric_runtime_metadata"><code>_get_fabric_runtime_metadata</code></a>
</li>
<li>
<a class="reference-chip" href="#_get_store"><code>_get_store</code></a>
</li>
<li>
<a class="reference-chip" href="#_load_and_validate_dataset_contract"><code>_load_and_validate_dataset_contract</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_load_dataset_contract"><code>_load_dataset_contract</code></a>, <a class="reference-chip" href="#_validate_dataset_contract"><code>_validate_dataset_contract</code></a>
</li>
<li>
<a class="reference-chip" href="#_load_dataset_contract"><code>_load_dataset_contract</code></a>
</li>
<li>
<a class="reference-chip" href="#_load_schema"><code>_load_schema</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_default_schema_text"><code>_default_schema_text</code></a>
</li>
<li>
<a class="reference-chip" href="#_normalize_name"><code>_normalize_name</code></a>
</li>
<li>
<a class="reference-chip" href="#_run_config_smoke_tests"><code>_run_config_smoke_tests</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_check_spark_session"><code>_check_spark_session</code></a>, <a class="reference-chip" href="#_get_fabric_runtime_metadata"><code>_get_fabric_runtime_metadata</code></a>, <a class="reference-chip" href="#_get_store"><code>_get_store</code></a>, <a class="reference-chip" href="#_validate_notebook_name"><code>_validate_notebook_name</code></a>
</li>
<li>
<a class="reference-chip" href="#_validate_dataset_contract"><code>_validate_dataset_contract</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_format_error_path"><code>_format_error_path</code></a>, <a class="reference-chip" href="#_load_schema"><code>_load_schema</code></a>
</li>
<li>
<a class="reference-chip" href="#_validate_framework_config"><code>_validate_framework_config</code></a>
</li>
<li>
<a class="reference-chip" href="#_validate_notebook_name"><code>_validate_notebook_name</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_normalize_name"><code>_normalize_name</code></a>
</li>
</ul>
</details>

### External callers

**fabric_input_output**
<a class="reference-chip" href="../../reference/read_lakehouse_csv/"><code>read_lakehouse_csv</code></a>, <a class="reference-chip" href="../../reference/read_lakehouse_excel/"><code>read_lakehouse_excel</code></a>, <a class="reference-chip" href="../../reference/read_lakehouse_parquet/"><code>read_lakehouse_parquet</code></a>, <a class="reference-chip" href="../../reference/read_lakehouse_table/"><code>read_lakehouse_table</code></a>, <a class="reference-chip" href="../../reference/read_warehouse_table/"><code>read_warehouse_table</code></a>, <a class="reference-chip" href="../../reference/write_lakehouse_table/"><code>write_lakehouse_table</code></a>, <a class="reference-chip" href="../../reference/write_warehouse_table/"><code>write_warehouse_table</code></a>

### External callees

**data_agreement**
<a class="reference-chip" href="../data_agreement/#_setup_data_agreement_tables"><code>_setup_data_agreement_tables</code></a>

**governance_review**
<a class="reference-chip" href="../governance_review/#_setup_governance_metadata_tables"><code>_setup_governance_metadata_tables</code></a>

**metadata**
<a class="reference-chip" href="../metadata/#_setup_notebook_registry_table"><code>_setup_notebook_registry_table</code></a>

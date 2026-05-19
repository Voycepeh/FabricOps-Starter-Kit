# `config` module

<div class="api-status-block">
  <span class="api-chip api-chip-module">Module overview</span>
</div>

## Module dependency summary

<div class="module-summary-cards"><span class="reference-chip">Callable count: 2</span><span class="reference-chip">Outbound: 0</span><span class="reference-chip">Inbound: 1</span></div>

## Module purpose

Owns environment setup, runtime initialization, paths, and notebook-wide configuration.

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
      <td><a href="../../reference/load_config/"><code>load_config</code></a></td>
      <td>Essential</td>
      <td>function</td>
      <td>Validate and return a user-supplied framework configuration.</td>
      <td><a href="../../reference/internal/config/_validate_framework_config/"><code>_validate_framework_config</code></a> (internal)</td>
    </tr>
    <tr>
      <td><a href="../../reference/setup_notebook/"><code>setup_notebook</code></a></td>
      <td>Essential</td>
      <td>function</td>
      <td>Run consolidated FabricOps startup for exploration and pipeline notebooks.</td>
      <td><a href="../../reference/internal/config/_get_store/"><code>_get_store</code></a> (internal), <a href="../../reference/internal/config/_run_config_smoke_tests/"><code>_run_config_smoke_tests</code></a> (internal)</td>
    </tr>
  </tbody>
</table>
</div>

## Advanced dependency sections


### Related internal helpers

<details>
<summary>Expand internal helper table</summary>

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
      <td><a href="../../reference/internal/config/_validate_framework_config/"><code>_validate_framework_config</code></a></td>
      <td><a href="../../reference/load_config/"><code>load_config</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/config/_validate_notebook_name/"><code>_validate_notebook_name</code></a></td>
      <td>—</td>
    </tr>
  </tbody>
</table>
</div>

</details>

### Callable relationships

<div class="module-relationship-list">
#### Module relationships
#### Functions in this module

<div class="callable-chip-group">
<a class="reference-chip" href="../modules/config/#_bootstrap_fabric_env"><code>_bootstrap_fabric_env</code></a> → <a class="reference-chip" href="../modules/config/#_get_fabric_runtime_metadata"><code>_get_fabric_runtime_metadata</code></a>
<a class="reference-chip" href="../modules/config/#_bootstrap_fabric_env"><code>_bootstrap_fabric_env</code></a> → <a class="reference-chip" href="../modules/config/#_get_store"><code>_get_store</code></a>
<a class="reference-chip" href="../modules/config/#_bootstrap_fabric_env"><code>_bootstrap_fabric_env</code></a> → <a class="reference-chip" href="../modules/config/#_run_config_smoke_tests"><code>_run_config_smoke_tests</code></a>
<a class="reference-chip" href="../modules/config/#_bootstrap_fabric_env"><code>_bootstrap_fabric_env</code></a> → <a class="reference-chip" href="../../reference/load_config/"><code>load_config</code></a>
<a class="reference-chip" href="../modules/config/#_load_schema"><code>_load_schema</code></a> → <a class="reference-chip" href="../modules/config/#_default_schema_text"><code>_default_schema_text</code></a>
<a class="reference-chip" href="../modules/config/#_run_config_smoke_tests"><code>_run_config_smoke_tests</code></a> → <a class="reference-chip" href="../modules/config/#_check_spark_session"><code>_check_spark_session</code></a>
<a class="reference-chip" href="../modules/config/#_run_config_smoke_tests"><code>_run_config_smoke_tests</code></a> → <a class="reference-chip" href="../modules/config/#_get_fabric_runtime_metadata"><code>_get_fabric_runtime_metadata</code></a>
<a class="reference-chip" href="../modules/config/#_run_config_smoke_tests"><code>_run_config_smoke_tests</code></a> → <a class="reference-chip" href="../modules/config/#_get_store"><code>_get_store</code></a>
<a class="reference-chip" href="../modules/config/#_run_config_smoke_tests"><code>_run_config_smoke_tests</code></a> → <a class="reference-chip" href="../modules/config/#_validate_notebook_name"><code>_validate_notebook_name</code></a>
<a class="reference-chip" href="../modules/config/#_validate_notebook_name"><code>_validate_notebook_name</code></a> → <a class="reference-chip" href="../modules/config/#_normalize_name"><code>_normalize_name</code></a>
<a class="reference-chip" href="../modules/config/#assert_valid_dataset_contract"><code>assert_valid_dataset_contract</code></a> → <a class="reference-chip" href="../modules/config/#validate_dataset_contract"><code>validate_dataset_contract</code></a>
<a class="reference-chip" href="../modules/config/#load_and_validate_dataset_contract"><code>load_and_validate_dataset_contract</code></a> → <a class="reference-chip" href="../modules/config/#load_dataset_contract"><code>load_dataset_contract</code></a>
<a class="reference-chip" href="../modules/config/#load_and_validate_dataset_contract"><code>load_and_validate_dataset_contract</code></a> → <a class="reference-chip" href="../modules/config/#validate_dataset_contract"><code>validate_dataset_contract</code></a>
<a class="reference-chip" href="../../reference/load_config/"><code>load_config</code></a> → <a class="reference-chip" href="../modules/config/#_validate_framework_config"><code>_validate_framework_config</code></a>
<a class="reference-chip" href="../../reference/setup_notebook/"><code>setup_notebook</code></a> → <a class="reference-chip" href="../modules/config/#_get_store"><code>_get_store</code></a>
<a class="reference-chip" href="../../reference/setup_notebook/"><code>setup_notebook</code></a> → <a class="reference-chip" href="../modules/config/#_run_config_smoke_tests"><code>_run_config_smoke_tests</code></a>
<a class="reference-chip" href="../../reference/setup_notebook/"><code>setup_notebook</code></a> → <a class="reference-chip" href="../../reference/load_config/"><code>load_config</code></a>
<a class="reference-chip" href="../modules/config/#validate_dataset_contract"><code>validate_dataset_contract</code></a> → <a class="reference-chip" href="../modules/config/#_format_error_path"><code>_format_error_path</code></a>
<a class="reference-chip" href="../modules/config/#validate_dataset_contract"><code>validate_dataset_contract</code></a> → <a class="reference-chip" href="../modules/config/#_load_schema"><code>_load_schema</code></a>
</div>
#### External callers

<div class="callable-chip-group">
<a class="reference-chip" href="../../reference/load_config/"><code>fabric_input_output.load_config</code></a>
<a class="reference-chip" href="../../reference/read_lakehouse_csv/"><code>fabric_input_output.read_lakehouse_csv</code></a>
<a class="reference-chip" href="../../reference/read_lakehouse_excel/"><code>fabric_input_output.read_lakehouse_excel</code></a>
<a class="reference-chip" href="../../reference/read_lakehouse_parquet/"><code>fabric_input_output.read_lakehouse_parquet</code></a>
<a class="reference-chip" href="../../reference/read_lakehouse_table/"><code>fabric_input_output.read_lakehouse_table</code></a>
<a class="reference-chip" href="../../reference/read_warehouse_table/"><code>fabric_input_output.read_warehouse_table</code></a>
<a class="reference-chip" href="../../reference/write_lakehouse_table/"><code>fabric_input_output.write_lakehouse_table</code></a>
<a class="reference-chip" href="../../reference/write_warehouse_table/"><code>fabric_input_output.write_warehouse_table</code></a>
</div>
#### External callees

None.
</div>

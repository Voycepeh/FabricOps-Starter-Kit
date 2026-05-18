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

<div class="module-mermaid-scroll module-diagram-desktop">
```mermaid
flowchart LR
  classDef currentModule fill:#fff3e0,stroke:#ef6c00,stroke-width:3px,color:#3e2723;
  classDef externalModule fill:#f5f5f5,stroke:#9e9e9e,stroke-width:1px,color:#616161;
  classDef currentCallable fill:#ffe0b2,stroke:#ef6c00,stroke-width:2px;
  classDef externalCallable fill:#eceff1,stroke:#90a4ae,stroke-width:1px;
  subgraph m_config[config]
    fabricops_kit_config__bootstrap_fabric_env["_bootstrap_fabric_env"]
    fabricops_kit_config__check_spark_session["_check_spark_session"]
    fabricops_kit_config__default_schema_text["_default_schema_text"]
    fabricops_kit_config__format_error_path["_format_error_path"]
    fabricops_kit_config__get_fabric_runtime_metadata["_get_fabric_runtime_metadata"]
    fabricops_kit_config__get_store["_get_store"]
    fabricops_kit_config__load_schema["_load_schema"]
    fabricops_kit_config__normalize_name["_normalize_name"]
    fabricops_kit_config__run_config_smoke_tests["_run_config_smoke_tests"]
    fabricops_kit_config__validate_framework_config["_validate_framework_config"]
    fabricops_kit_config__validate_notebook_name["_validate_notebook_name"]
    fabricops_kit_config_assert_valid_dataset_contract["assert_valid_dataset_contract"]
    fabricops_kit_config_load_and_validate_dataset_contract["load_and_validate_dataset_contract"]
    fabricops_kit_config_load_config["load_config"]
    fabricops_kit_config_load_dataset_contract["load_dataset_contract"]
    fabricops_kit_config_setup_notebook["setup_notebook"]
    fabricops_kit_config_validate_dataset_contract["validate_dataset_contract"]
  end
  subgraph m_fabric_input_output[fabric_input_output]
    fabricops_kit_fabric_input_output_load_config["load_config"]
    fabricops_kit_fabric_input_output_read_lakehouse_csv["read_lakehouse_csv"]
    fabricops_kit_fabric_input_output_read_lakehouse_excel["read_lakehouse_excel"]
    fabricops_kit_fabric_input_output_read_lakehouse_parquet["read_lakehouse_parquet"]
    fabricops_kit_fabric_input_output_read_lakehouse_table["read_lakehouse_table"]
    fabricops_kit_fabric_input_output_read_warehouse_table["read_warehouse_table"]
    fabricops_kit_fabric_input_output_write_lakehouse_table["write_lakehouse_table"]
    fabricops_kit_fabric_input_output_write_warehouse_table["write_warehouse_table"]
  end
  fabricops_kit_config__bootstrap_fabric_env --> fabricops_kit_config__get_fabric_runtime_metadata
  fabricops_kit_config__bootstrap_fabric_env --> fabricops_kit_config__get_store
  fabricops_kit_config__bootstrap_fabric_env --> fabricops_kit_config__run_config_smoke_tests
  fabricops_kit_config__bootstrap_fabric_env --> fabricops_kit_config_load_config
  fabricops_kit_config__load_schema --> fabricops_kit_config__default_schema_text
  fabricops_kit_config__run_config_smoke_tests --> fabricops_kit_config__check_spark_session
  fabricops_kit_config__run_config_smoke_tests --> fabricops_kit_config__get_fabric_runtime_metadata
  fabricops_kit_config__run_config_smoke_tests --> fabricops_kit_config__get_store
  fabricops_kit_config__run_config_smoke_tests --> fabricops_kit_config__validate_notebook_name
  fabricops_kit_config__validate_notebook_name --> fabricops_kit_config__normalize_name
  fabricops_kit_config_assert_valid_dataset_contract --> fabricops_kit_config_validate_dataset_contract
  fabricops_kit_config_load_and_validate_dataset_contract --> fabricops_kit_config_load_dataset_contract
  fabricops_kit_config_load_and_validate_dataset_contract --> fabricops_kit_config_validate_dataset_contract
  fabricops_kit_config_load_config --> fabricops_kit_config__validate_framework_config
  fabricops_kit_config_setup_notebook --> fabricops_kit_config__get_store
  fabricops_kit_config_setup_notebook --> fabricops_kit_config__run_config_smoke_tests
  fabricops_kit_config_setup_notebook --> fabricops_kit_config_load_config
  fabricops_kit_config_validate_dataset_contract --> fabricops_kit_config__format_error_path
  fabricops_kit_config_validate_dataset_contract --> fabricops_kit_config__load_schema
  fabricops_kit_fabric_input_output_load_config --> fabricops_kit_config_load_config
  fabricops_kit_fabric_input_output_read_lakehouse_csv --> fabricops_kit_config__get_store
  fabricops_kit_fabric_input_output_read_lakehouse_excel --> fabricops_kit_config__get_store
  fabricops_kit_fabric_input_output_read_lakehouse_parquet --> fabricops_kit_config__get_store
  fabricops_kit_fabric_input_output_read_lakehouse_table --> fabricops_kit_config__get_store
  fabricops_kit_fabric_input_output_read_warehouse_table --> fabricops_kit_config__get_store
  fabricops_kit_fabric_input_output_write_lakehouse_table --> fabricops_kit_config__get_store
  fabricops_kit_fabric_input_output_write_warehouse_table --> fabricops_kit_config__get_store
  class m_config currentModule;
  class m_fabric_input_output externalModule;
  class fabricops_kit_config__bootstrap_fabric_env,fabricops_kit_config__check_spark_session,fabricops_kit_config__default_schema_text,fabricops_kit_config__format_error_path,fabricops_kit_config__get_fabric_runtime_metadata,fabricops_kit_config__get_store,fabricops_kit_config__load_schema,fabricops_kit_config__normalize_name,fabricops_kit_config__run_config_smoke_tests,fabricops_kit_config__validate_framework_config,fabricops_kit_config__validate_notebook_name,fabricops_kit_config_assert_valid_dataset_contract,fabricops_kit_config_load_and_validate_dataset_contract,fabricops_kit_config_load_config,fabricops_kit_config_load_dataset_contract,fabricops_kit_config_setup_notebook,fabricops_kit_config_validate_dataset_contract currentCallable;
  class fabricops_kit_fabric_input_output_load_config,fabricops_kit_fabric_input_output_read_lakehouse_csv,fabricops_kit_fabric_input_output_read_lakehouse_excel,fabricops_kit_fabric_input_output_read_lakehouse_parquet,fabricops_kit_fabric_input_output_read_lakehouse_table,fabricops_kit_fabric_input_output_read_warehouse_table,fabricops_kit_fabric_input_output_write_lakehouse_table,fabricops_kit_fabric_input_output_write_warehouse_table externalCallable;
```
</div>

<div class="module-relationship-list module-diagram-mobile">
#### Inside this module

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
#### Used by other modules

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
#### Uses other modules

None.
</div>

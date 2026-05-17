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

### Module internal callable dependencies

<details>
<summary>Expand module internal callable graph</summary>

<div class="module-mermaid-scroll">
```mermaid
flowchart LR
  n1["config._bootstrap_fabric_env"] --> n1b["config._get_fabric_runtime_metadata"]
  n2["config._bootstrap_fabric_env"] --> n2b["config._get_store"]
  n3["config._bootstrap_fabric_env"] --> n3b["config._run_config_smoke_tests"]
  n4["config._bootstrap_fabric_env"] --> n4b["config.load_config"]
  n5["config._load_schema"] --> n5b["config._default_schema_text"]
  n6["config._run_config_smoke_tests"] --> n6b["config._check_spark_session"]
  n7["config._run_config_smoke_tests"] --> n7b["config._get_fabric_runtime_metadata"]
  n8["config._run_config_smoke_tests"] --> n8b["config._get_store"]
  n9["config._run_config_smoke_tests"] --> n9b["config._validate_notebook_name"]
  n10["config._validate_notebook_name"] --> n10b["config._normalize_name"]
  n11["config.assert_valid_dataset_contract"] --> n11b["config.validate_dataset_contract"]
  n12["config.load_and_validate_dataset_contract"] --> n12b["config.load_dataset_contract"]
  n13["config.load_and_validate_dataset_contract"] --> n13b["config.validate_dataset_contract"]
  n14["config.load_config"] --> n14b["config._validate_framework_config"]
  n15["config.setup_notebook"] --> n15b["config._get_store"]
  n16["config.setup_notebook"] --> n16b["config._run_config_smoke_tests"]
  n17["config.setup_notebook"] --> n17b["config.load_config"]
  n18["config.validate_dataset_contract"] --> n18b["config._format_error_path"]
  n19["config.validate_dataset_contract"] --> n19b["config._load_schema"]
```
</div>

</details>

### Outbound

No outbound references detected.

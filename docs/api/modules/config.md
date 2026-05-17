# `config` module

<div class="api-status-block">
  <span class="api-chip api-chip-module">Module overview</span>
</div>

## Module dependency summary

<div class="module-table-scroll">
| Callable count | Internal helper count | Outbound references | Inbound references |
|---:|---:|---:|---:|
| 2 | 13 | 0 | 1 |
</div>

## Module purpose

Owns environment setup, runtime initialization, paths, and notebook-wide configuration.

## Public callables

<div class="module-table-scroll">
| Callable | Tier | Type | Summary | Related helpers |
|---|---|---|---|---|
| [`load_config`](../../reference/load_config/) | Essential | function | Validate and return a user-supplied framework configuration. | [`_validate_framework_config`](../../reference/internal/config/_validate_framework_config/) (internal) |
| [`setup_notebook`](../../reference/setup_notebook/) | Essential | function | Run consolidated FabricOps startup for exploration and pipeline notebooks. | [`_get_store`](../../reference/internal/config/_get_store/) (internal), [`_run_config_smoke_tests`](../../reference/internal/config/_run_config_smoke_tests/) (internal) |
</div>

## Advanced dependency sections


### Related internal helpers

<details>
<summary>Expand internal helper table</summary>

<div class="module-table-scroll">
| Helper | Related public callables |
|---|---|
| [`_bootstrap_fabric_env`](../../reference/internal/config/_bootstrap_fabric_env/) | — |
| [`_check_fabric_ai_functions_available`](../../reference/internal/config/_check_fabric_ai_functions_available/) | — |
| [`_check_spark_session`](../../reference/internal/config/_check_spark_session/) | — |
| [`_configure_fabric_ai_functions`](../../reference/internal/config/_configure_fabric_ai_functions/) | — |
| [`_default_schema_text`](../../reference/internal/config/_default_schema_text/) | — |
| [`_format_error_path`](../../reference/internal/config/_format_error_path/) | — |
| [`_get_fabric_runtime_metadata`](../../reference/internal/config/_get_fabric_runtime_metadata/) | — |
| [`_get_store`](../../reference/internal/config/_get_store/) | [`setup_notebook`](../../reference/setup_notebook/) |
| [`_load_schema`](../../reference/internal/config/_load_schema/) | — |
| [`_normalize_name`](../../reference/internal/config/_normalize_name/) | — |
| [`_run_config_smoke_tests`](../../reference/internal/config/_run_config_smoke_tests/) | [`setup_notebook`](../../reference/setup_notebook/) |
| [`_validate_framework_config`](../../reference/internal/config/_validate_framework_config/) | [`load_config`](../../reference/load_config/) |
| [`_validate_notebook_name`](../../reference/internal/config/_validate_notebook_name/) | — |
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

### Cross-module references

No cross-module references detected.

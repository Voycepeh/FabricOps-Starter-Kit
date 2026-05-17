# `config` module

<div class="api-status-block">
  <span class="api-chip api-chip-module">Module overview</span>
</div>

## Module dependency summary

- **Essential:** 2
- **Optional:** 0
- **Internal:** 13
- **Depends On:** 0 modules
- **Used By:** 1 modules

## Essential callables

| Callable | Type | Summary | Related helpers |
|---|---|---|---|
| [`load_config`](../../reference/load_config/) | function | Validate and return a user-supplied framework configuration. | [`_validate_framework_config`](../../reference/internal/config/_validate_framework_config/) (internal) |
| [`setup_notebook`](../../reference/setup_notebook/) | function | Run consolidated FabricOps startup for exploration and pipeline notebooks. | [`_get_store`](../../reference/internal/config/_get_store/) (internal), [`_run_config_smoke_tests`](../../reference/internal/config/_run_config_smoke_tests/) (internal) |

## Optional callables

No advanced helpers listed for this module.

## Related internal helpers

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

## Module internal callable graph

```mermaid
flowchart LR
  _validate_framework_config --> FrameworkConfig
  _validate_framework_config --> keys
  load_config --> _validate_framework_config
  _validate_notebook_name --> _normalize_name
  _run_config_smoke_tests --> _check_spark_session
  _run_config_smoke_tests --> _get_fabric_runtime_metadata
  _run_config_smoke_tests --> ConfigSmokeCheckResult
  _run_config_smoke_tests --> ConfigSmokeCheckResult
  _run_config_smoke_tests --> _validate_notebook_name
  _run_config_smoke_tests --> _get_store
  _run_config_smoke_tests --> ConfigSmokeCheckResult
  _run_config_smoke_tests --> ConfigSmokeCheckResult
  _run_config_smoke_tests --> ConfigSmokeCheckResult
  _run_config_smoke_tests --> ConfigSmokeCheckResult
  _run_config_smoke_tests --> ConfigSmokeCheckResult
  _run_config_smoke_tests --> ConfigSmokeCheckResult
  _run_config_smoke_tests --> ConfigSmokeCheckResult
  _run_config_smoke_tests --> ConfigSmokeCheckResult
  _run_config_smoke_tests --> ConfigSmokeCheckResult
  _bootstrap_fabric_env --> _get_fabric_runtime_metadata
  _bootstrap_fabric_env --> ConfigBootstrapResult
  _bootstrap_fabric_env --> load_config
  _bootstrap_fabric_env --> _get_store
  _bootstrap_fabric_env --> _run_config_smoke_tests
  setup_notebook --> load_config
  setup_notebook --> _run_config_smoke_tests
  setup_notebook --> NotebookSetupContext
  setup_notebook --> _get_store
  _load_schema --> _default_schema_text
  validate_dataset_contract --> _load_schema
  validate_dataset_contract --> _format_error_path
  assert_valid_dataset_contract --> validate_dataset_contract
  assert_valid_dataset_contract --> DatasetContractValidationError
  load_and_validate_dataset_contract --> load_dataset_contract
  load_and_validate_dataset_contract --> validate_dataset_contract
```

## Cross-module callable graph

```mermaid
flowchart LR
  no_cross_edges[No cross-module callable edges detected]
```

# setup_notebook

**Module:** `config`  
**Classification:** Callable

## Status

Public callable helper intended for notebook authors.

## When to use this

Use at the start of 00_env_config or a notebook template to validate FabricOps configuration, resolve required targets, and capture runtime context before other helpers run.

## When not to use this

Do not use as a replacement for metadata table setup or per-table governance writes; call setup_metadata_tables for metadata storage preparation.

## Quick example

context = setup_notebook(CONFIG, env="Sandbox", required_targets=["Source", "Unified"], notebook_name="00_env_config")

## Signature

```python
def setup_notebook(config: FrameworkConfig | dict[str, Any], env: str='Sandbox', required_targets: list[str] | None=None, notebook_name: str | None=None, run_id_prefix: str='run', local_fallback_name: str | None=None) -> NotebookSetupContext
```

## Parameters

config, env, optional required_targets, notebook_name, run_id_prefix, and local_fallback_name that define the runtime setup context.

## Returns

NotebookSetupContext with resolved configuration paths, runtime metadata, smoke-check results, and readiness status.

## Raises

ValueError for invalid configuration sections, missing required paths, or unresolved required targets.

## Side effects

Runs configuration validation and Fabric readiness checks; it does not write FabricOps metadata tables.

## FabricOps context

Requires the FrameworkConfig or compatible CONFIG from 00_env_config plus the intended env name; never hardcode Fabric workspace or item identifiers.

## AI implementation contract

- **required_context:** Requires the FrameworkConfig or compatible CONFIG from 00_env_config plus the intended env name; never hardcode Fabric workspace or item identifiers.
- **inputs:** config, env, optional required_targets, notebook_name, run_id_prefix, and local_fallback_name that define the runtime setup context.
- **output:** NotebookSetupContext with resolved configuration paths, runtime metadata, smoke-check results, and readiness status.
- **side_effects:** Runs configuration validation and Fabric readiness checks; it does not write FabricOps metadata tables.
- **failure_modes:** ValueError for invalid configuration sections, missing required paths, or unresolved required targets.
- **verification:** Verify the returned context is ready before generating downstream notebook code and confirm required targets resolve for the selected env.

## Related functions

- <a href="../setup_metadata_tables/"><code>fabricops_kit.config.setup_metadata_tables</code></a>

## Source and tests

- Source file path: `src/fabricops_kit/config.py`
- Source reference: <a href="../../api/modules/config/#setup_notebook">Module source anchor</a>
- Tests: Not documented yet

## Function manifest

- Fully qualified function name: `fabricops_kit.config.setup_notebook`
- Short name: `setup_notebook`
- Module: `config`
- Classification: Callable
- Related module: `config`
- Inbound references count: 0
- Outbound references count: 4

## Outbound references
- <a href="../internal/config_NotebookSetupContext/"><code>fabricops_kit.config.NotebookSetupContext</code></a>
- <a href="../internal/config__get_store/"><code>fabricops_kit.config._get_store</code></a>
- <a href="../internal/config__run_config_smoke_tests/"><code>fabricops_kit.config._run_config_smoke_tests</code></a>
- <a href="../internal/config__validate_framework_config/"><code>fabricops_kit.config._validate_framework_config</code></a>

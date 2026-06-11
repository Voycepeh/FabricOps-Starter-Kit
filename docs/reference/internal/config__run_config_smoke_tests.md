# _run_config_smoke_tests

**Module:** `config`
**Classification:** Internal

## Status

Internal helper used by the package implementation.

## Function type: Internal helper

Internal helper

## Direct use: No

Do not call this helper directly from notebooks; use the public callable helpers instead.

## Used by

- <a href="../setup_notebook/"><code>fabricops_kit.config.setup_notebook</code></a>

## Purpose

Run 00_env_config readiness smoke checks for configuration bootstrap.

## Signature if available

```python
def _run_config_smoke_tests(config: FrameworkConfig, env: str='Sandbox', required_targets: list[str] | None=None, check_io_import: bool=False, notebook_name: str | None=None) -> list[ConfigSmokeCheckResult]
```

## Side effects

Not documented yet

## Maintainer notes

Maintain this helper through the owning implementation module and keep generated references in sync.

## AI implementation contract

Use internal pages only for package maintenance. Prefer public callable pages when authoring notebooks.

## Function manifest

- Fully qualified function name: `fabricops_kit.config._run_config_smoke_tests`
- Short name: `_run_config_smoke_tests`
- Module: `config`
- Classification: Internal
- Related module: `config`
- Source file path: `src/fabricops_kit/config.py`
- Source reference: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/8f8ba1a4c1e063896508520952dedc3eda348629/src/fabricops_kit/config.py#L675-L774">View source on GitHub</a>
- Inbound references count: 1
- Outbound references count: 5

## Inbound references
- <a href="../setup_notebook/"><code>fabricops_kit.config.setup_notebook</code></a>

## Outbound references
- <a href="../internal/config_ConfigSmokeCheckResult/"><code>fabricops_kit.config.ConfigSmokeCheckResult</code></a>
- <a href="../internal/config__check_spark_session/"><code>fabricops_kit.config._check_spark_session</code></a>
- <a href="../internal/config__get_fabric_runtime_metadata/"><code>fabricops_kit.config._get_fabric_runtime_metadata</code></a>
- <a href="../internal/config__get_store/"><code>fabricops_kit.config._get_store</code></a>
- <a href="../internal/config__validate_notebook_name/"><code>fabricops_kit.config._validate_notebook_name</code></a>

# setup_notebook

**Module:** `config`  
**Classification:** Callable

## Status

Public callable helper intended for notebook authors.

## When to use this

Shared environment setup and runtime validation for notebook templates.

## When not to use this

Not documented yet

## Quick example

Not documented yet

## Signature

```python
def setup_notebook(config: FrameworkConfig | dict[str, Any], env: str='Sandbox', required_targets: list[str] | None=None, notebook_name: str | None=None, run_id_prefix: str='run', local_fallback_name: str | None=None) -> NotebookSetupContext
```

## Parameters

config : FrameworkConfig | dict[str, Any]
    Framework configuration object or compatible mapping. The setup flow
    validates required sections and configured Fabric targets before
    running readiness checks.
env : str, default="Sandbox"
    Environment key used to resolve target paths.
required_targets : list[str] | None, optional
    Target names that must resolve for ``env``. Defaults to
    ``["Source", "Unified"]``.
notebook_name : str | None, optional
    Explicit notebook name used for runtime metadata and naming checks.
run_id_prefix : str, default="run"
    Prefix used when a Fabric runtime run identifier is unavailable.
local_fallback_name : str | None, optional
    Notebook name used when neither ``notebook_name`` nor Fabric runtime
    context provides one.

## Returns

NotebookSetupContext
    Validated runtime context with resolved paths, smoke-check results,
    runtime metadata, and overall readiness status.

## Raises

ValueError
    Raised when config sections are invalid or required targets cannot be
    resolved for the selected environment.

## Side effects

Not documented yet

## FabricOps context

Starter template: `00_env_config`; segment: `Environment bootstrap`.

## AI implementation contract

Not documented yet

## Related functions

- <a href="../internal/config_NotebookSetupContext/"><code>fabricops_kit.config.NotebookSetupContext</code></a>
- <a href="../internal/config__get_store/"><code>fabricops_kit.config._get_store</code></a>
- <a href="../internal/config__run_config_smoke_tests/"><code>fabricops_kit.config._run_config_smoke_tests</code></a>
- <a href="../internal/config__validate_framework_config/"><code>fabricops_kit.config._validate_framework_config</code></a>

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

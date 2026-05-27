# setup_notebook

## Template step
00_env_config

## Function role
Template entrypoint

## Use this when
Use `setup_notebook` during template-driven notebook execution.

## What it delegates to

### Callable functions called
- `fabricops_kit.config.load_config`

### Internal helpers used
- `fabricops_kit.config.NotebookSetupContext`
- `fabricops_kit.config._get_store`
- `fabricops_kit.config._run_config_smoke_tests`

## Debug this function when
- notebook startup checks fail
- runtime capabilities are missing

## Agent repair guide
1. Preserve public callable signature unless templates are updated.
2. Inspect delegated helpers before rewriting wrapper logic.
3. Preserve output shape where downstream notebooks depend on it.
4. Update tests and templates together if behavior changes.

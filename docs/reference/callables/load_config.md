# load_config

## Template step
00_env_config

## Function role
Callable orchestration wrapper

## Use this when
Use `load_config` during template-driven notebook execution.

## What it delegates to

### Callable functions called
- None

### Internal helpers used
- `fabricops_kit.config._validate_framework_config`

## Debug this function when
- resolved paths are incorrect
- environment mapping is missing

## Agent repair guide
1. Preserve public callable signature unless templates are updated.
2. Inspect delegated helpers before rewriting wrapper logic.
3. Preserve output shape where downstream notebooks depend on it.
4. Update tests and templates together if behavior changes.

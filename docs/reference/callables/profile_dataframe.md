# profile_dataframe

## Template step
02_exploration

## Function role
Validation/check function

## Use this when
Use `profile_dataframe` during template-driven notebook execution.

## What it delegates to

### Callable functions called
- None

### Internal helpers used
- `fabricops_kit.data_profiling._get_profiled_columns`
- `fabricops_kit.data_profiling._is_min_max_supported_type`

## Debug this function when
- profile metrics look inconsistent
- profile output schema changed unexpectedly

## Agent repair guide
1. Preserve public callable signature unless templates are updated.
2. Inspect delegated helpers before rewriting wrapper logic.
3. Preserve output shape where downstream notebooks depend on it.
4. Update tests and templates together if behavior changes.

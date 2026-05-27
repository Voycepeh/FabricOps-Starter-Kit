# read_lakehouse_table

## Template step
02_exploration

## Function role
Callable utility

## Use this when
Use `read_lakehouse_table` during template-driven notebook execution.

## What it delegates to

### Callable functions called
- None

### Internal helpers used
- `fabricops_kit.config._get_store`
- `fabricops_kit.fabric_input_output._get_spark`

## Debug this function when
- metadata table was not read
- table path resolution fails

## Agent repair guide
1. Preserve public callable signature unless templates are updated.
2. Inspect delegated helpers before rewriting wrapper logic.
3. Preserve output shape where downstream notebooks depend on it.
4. Update tests and templates together if behavior changes.

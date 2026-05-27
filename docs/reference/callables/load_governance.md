# load_governance

## Template step
Governance/classification

## Function role
Callable utility

## Use this when
Use `load_governance` during template-driven notebook execution.

## What it delegates to

### Callable functions called
- None

### Internal helpers used
- `fabricops_kit.data_governance._coerce_row_dicts`

## Debug this function when
- governance metadata fails to load

## Agent repair guide
1. Preserve public callable signature unless templates are updated.
2. Inspect delegated helpers before rewriting wrapper logic.
3. Preserve output shape where downstream notebooks depend on it.
4. Update tests and templates together if behavior changes.

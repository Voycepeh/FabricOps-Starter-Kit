# load_agreements

## Template step
—

## Function role
Callable orchestration wrapper

## Use this when
Use `load_agreements` during template-driven notebook execution.

## What it delegates to

### Callable functions called
- None

### Internal helpers used
- `fabricops_kit.data_agreement._coerce_row_dicts`
- `fabricops_kit.data_agreement._latest_distinct_agreements`

## Debug this function when
- Output shape or metadata evidence is unexpected.

## Agent repair guide
1. Preserve public callable signature unless templates are updated.
2. Inspect delegated helpers before rewriting wrapper logic.
3. Preserve output shape where downstream notebooks depend on it.
4. Update tests and templates together if behavior changes.

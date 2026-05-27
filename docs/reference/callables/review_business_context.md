# review_business_context

## Template step
—

## Function role
Callable orchestration wrapper

## Use this when
Use `review_business_context` during template-driven notebook execution.

## What it delegates to

### Callable functions called
- None

### Internal helpers used
- `fabricops_kit.business_context._require_ipywidgets`
- `fabricops_kit.metadata.build_metadata_column_key`
- `fabricops_kit.metadata.build_metadata_table_key`

## Debug this function when
- Output shape or metadata evidence is unexpected.

## Agent repair guide
1. Preserve public callable signature unless templates are updated.
2. Inspect delegated helpers before rewriting wrapper logic.
3. Preserve output shape where downstream notebooks depend on it.
4. Update tests and templates together if behavior changes.

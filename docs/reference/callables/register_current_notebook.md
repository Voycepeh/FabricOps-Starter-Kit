# register_current_notebook

## Template step
—

## Function role
Callable orchestration wrapper

## Use this when
Use `register_current_notebook` during template-driven notebook execution.

## What it delegates to

### Callable functions called
- None

### Internal helpers used
- `fabricops_kit.metadata._context_get`
- `fabricops_kit.metadata._runtime_context`
- `fabricops_kit.metadata._safe_str`
- `fabricops_kit.metadata.write_metadata_rows`

## Debug this function when
- Output shape or metadata evidence is unexpected.

## Agent repair guide
1. Preserve public callable signature unless templates are updated.
2. Inspect delegated helpers before rewriting wrapper logic.
3. Preserve output shape where downstream notebooks depend on it.
4. Update tests and templates together if behavior changes.

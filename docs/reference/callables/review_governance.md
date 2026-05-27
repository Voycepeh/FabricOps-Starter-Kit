# review_governance

## Template step
—

## Function role
Callable orchestration wrapper

## Use this when
Use `review_governance` during template-driven notebook execution.

## What it delegates to

### Callable functions called
- None

### Internal helpers used
- `fabricops_kit.data_governance._undo_last_action`
- `fabricops_kit.metadata._now_utc_iso`
- `fabricops_kit.metadata.build_metadata_column_key`
- `fabricops_kit.metadata.build_metadata_table_key`

## Debug this function when
- Output shape or metadata evidence is unexpected.

## Agent repair guide
1. Preserve public callable signature unless templates are updated.
2. Inspect delegated helpers before rewriting wrapper logic.
3. Preserve output shape where downstream notebooks depend on it.
4. Update tests and templates together if behavior changes.

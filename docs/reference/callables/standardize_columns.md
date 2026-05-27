# standardize_columns

## Template step
03_pipeline_contract

## Function role
Callable utility

## Use this when
Use `standardize_columns` during template-driven notebook execution.

## What it delegates to

### Callable functions called
- None

### Internal helpers used
- `fabricops_kit.technical_columns._add_audit_columns`
- `fabricops_kit.technical_columns._add_datetime_features`
- `fabricops_kit.technical_columns._add_hash_columns`

## Debug this function when
- standardized output columns are missing

## Agent repair guide
1. Preserve public callable signature unless templates are updated.
2. Inspect delegated helpers before rewriting wrapper logic.
3. Preserve output shape where downstream notebooks depend on it.
4. Update tests and templates together if behavior changes.

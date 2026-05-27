# assert_dq_passed

## Template step
03_pipeline_contract

## Function role
Validation/check function

## Use this when
Use `assert_dq_passed` during template-driven notebook execution.

## What it delegates to

### Callable functions called
- None

### Internal helpers used
- None

## Debug this function when
- pipeline succeeds when DQ should fail

## Agent repair guide
1. Preserve public callable signature unless templates are updated.
2. Inspect delegated helpers before rewriting wrapper logic.
3. Preserve output shape where downstream notebooks depend on it.
4. Update tests and templates together if behavior changes.

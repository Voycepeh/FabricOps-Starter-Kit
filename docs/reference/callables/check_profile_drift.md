# check_profile_drift

## Template step
Drift enforcement

## Function role
Validation/check function

## Use this when
Use `check_profile_drift` during template-driven notebook execution.

## What it delegates to

### Callable functions called
- None

### Internal helpers used
- None

## Debug this function when
- profile drift alerts are missing or noisy

## Agent repair guide
1. Preserve public callable signature unless templates are updated.
2. Inspect delegated helpers before rewriting wrapper logic.
3. Preserve output shape where downstream notebooks depend on it.
4. Update tests and templates together if behavior changes.

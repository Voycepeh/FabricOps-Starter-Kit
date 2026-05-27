# check_partition_drift

## Template step
Drift enforcement

## Function role
Validation/check function

## Use this when
Use `check_partition_drift` during template-driven notebook execution.

## What it delegates to

### Callable functions called
- None

### Internal helpers used
- `fabricops_kit.drift.build_partition_snapshot`
- `fabricops_kit.drift.compare_partition_snapshots`
- `fabricops_kit.drift.default_incremental_safety_policy`

## Debug this function when
- partition freshness or counts look wrong

## Agent repair guide
1. Preserve public callable signature unless templates are updated.
2. Inspect delegated helpers before rewriting wrapper logic.
3. Preserve output shape where downstream notebooks depend on it.
4. Update tests and templates together if behavior changes.

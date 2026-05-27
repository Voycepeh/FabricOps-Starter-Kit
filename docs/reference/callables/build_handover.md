# build_handover

## Template step
Handover/run summary

## Function role
Callable orchestration wrapper

## Use this when
Use `build_handover` during template-driven notebook execution.

## What it delegates to

### Callable functions called
- None

### Internal helpers used
- None

## Debug this function when
- handover summary misses required sections

## Agent repair guide
1. Preserve public callable signature unless templates are updated.
2. Inspect delegated helpers before rewriting wrapper logic.
3. Preserve output shape where downstream notebooks depend on it.
4. Update tests and templates together if behavior changes.

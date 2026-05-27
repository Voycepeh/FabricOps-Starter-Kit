# render_handover_markdown

## Template step
Handover/run summary

## Function role
Callable utility

## Use this when
Use `render_handover_markdown` during template-driven notebook execution.

## What it delegates to

### Callable functions called
- None

### Internal helpers used
- `fabricops_kit.handover._status_of`

## Debug this function when
- markdown rendering fails
- JSON serialization failed

## Agent repair guide
1. Preserve public callable signature unless templates are updated.
2. Inspect delegated helpers before rewriting wrapper logic.
3. Preserve output shape where downstream notebooks depend on it.
4. Update tests and templates together if behavior changes.

# review_dq_rules

## Template step
Data quality review

## Function role
Review/approval function

## Use this when
Use `review_dq_rules` during template-driven notebook execution.

## What it delegates to

### Callable functions called
- None

### Internal helpers used
- `fabricops_kit.data_quality._require_ipywidgets`

## Debug this function when
- review workflow misses required rule fields

## Agent repair guide
1. Preserve public callable signature unless templates are updated.
2. Inspect delegated helpers before rewriting wrapper logic.
3. Preserve output shape where downstream notebooks depend on it.
4. Update tests and templates together if behavior changes.

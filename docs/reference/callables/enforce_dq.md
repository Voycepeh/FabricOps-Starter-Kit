# enforce_dq

## Template step
03_pipeline_contract

## Function role
Callable orchestration wrapper

## Use this when
Use `enforce_dq` during template-driven notebook execution.

## What it delegates to

### Callable functions called
- `fabricops_kit.data_quality.validate_dq_rules`

### Internal helpers used
- `fabricops_kit.data_quality.DQEnforcementResult`
- `fabricops_kit.data_quality._load_active_dq_rules`
- `fabricops_kit.data_quality._run_dq_rules`
- `fabricops_kit.data_quality._split_dq_rows`

## Debug this function when
- DQ rules look wrong
- quarantine split is unexpected

## Agent repair guide
1. Preserve public callable signature unless templates are updated.
2. Inspect delegated helpers before rewriting wrapper logic.
3. Preserve output shape where downstream notebooks depend on it.
4. Update tests and templates together if behavior changes.

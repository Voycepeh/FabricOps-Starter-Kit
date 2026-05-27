# write_dq_rules

## Template step
Data quality review

## Function role
Evidence writer

## Use this when
Use `write_dq_rules` during template-driven notebook execution.

## What it delegates to

### Callable functions called
- `fabricops_kit.data_quality.validate_dq_rules`
- `fabricops_kit.fabric_input_output.write_lakehouse_table`

### Internal helpers used
- `fabricops_kit.data_quality._build_dq_rule_history`

## Debug this function when
- metadata table was not written
- rule versioning appears wrong

## Agent repair guide
1. Preserve public callable signature unless templates are updated.
2. Inspect delegated helpers before rewriting wrapper logic.
3. Preserve output shape where downstream notebooks depend on it.
4. Update tests and templates together if behavior changes.

# draft_dq_rules

## Template step
02_exploration

## Function role
AI-assisted suggestion function

## Use this when
Use `draft_dq_rules` during template-driven notebook execution.

## What it delegates to

### Callable functions called
- None

### Internal helpers used
- `fabricops_kit.data_quality._extract_dq_rules`
- `fabricops_kit.data_quality._prepare_dq_profile_input_rows`
- `fabricops_kit.data_quality._suggest_dq_rules`

## Debug this function when
- AI-generated rules do not match business expectations
- suggested rules are too generic

## Agent repair guide
1. Preserve public callable signature unless templates are updated.
2. Inspect delegated helpers before rewriting wrapper logic.
3. Preserve output shape where downstream notebooks depend on it.
4. Update tests and templates together if behavior changes.

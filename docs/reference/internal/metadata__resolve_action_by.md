# _resolve_action_by

## Internal helper
Internal helper. Do not call directly from notebooks unless extending FabricOps.

## Purpose
Supports callable orchestration internals.

## Used by callable functions
- None

## Used by internal helpers
- `fabricops_kit.data_governance._approved_widget_rows`
- `fabricops_kit.data_quality._build_dq_rule_deactivation_metadata_df`
- `fabricops_kit.data_quality._build_dq_rule_deactivations`
- `fabricops_kit.data_quality._build_dq_rule_history`
- `fabricops_kit.data_quality._build_dq_rules_metadata_df`

## Debug relevance
Inspect this helper when parent callable outputs are malformed, missing evidence, or failing validation.

## Safe change guidance
Preserve helper contract, return shape, and side effects expected by parent callables.

# _latest_dq_rule_versions

## Internal helper
Internal helper. Do not call directly from notebooks unless extending FabricOps.

## Purpose
Supports callable orchestration internals.

## Used by callable functions
- None

## Used by internal helpers
- `fabricops_kit.data_quality._load_active_dq_rule_metadata`
- `fabricops_kit.data_quality._load_active_dq_rules`

## Debug relevance
Inspect this helper when parent callable outputs are malformed, missing evidence, or failing validation.

## Safe change guidance
Preserve helper contract, return shape, and side effects expected by parent callables.

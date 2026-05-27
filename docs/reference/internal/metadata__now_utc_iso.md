# _now_utc_iso

## Internal helper
Internal helper. Do not call directly from notebooks unless extending FabricOps.

## Purpose
Supports callable orchestration internals.

## Used by callable functions
- `fabricops_kit.data_governance.review_governance`

## Used by internal helpers
- `fabricops_kit.data_quality._build_dq_rule_deactivation_metadata_df`
- `fabricops_kit.data_quality._build_dq_rules_metadata_df`
- `fabricops_kit.metadata.build_evidence_row`

## Debug relevance
Inspect this helper when parent callable outputs are malformed, missing evidence, or failing validation.

## Safe change guidance
Preserve helper contract, return shape, and side effects expected by parent callables.

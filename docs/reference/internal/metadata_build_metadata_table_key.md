# build_metadata_table_key

## Internal helper
Internal helper. Do not call directly from notebooks unless extending FabricOps.

## Purpose
Supports callable orchestration internals.

## Used by callable functions
- `fabricops_kit.business_context.review_business_context`
- `fabricops_kit.data_governance.review_governance`

## Used by internal helpers
- `fabricops_kit.data_quality._attach_rule_metadata_keys`

## Debug relevance
Inspect this helper when parent callable outputs are malformed, missing evidence, or failing validation.

## Safe change guidance
Preserve helper contract, return shape, and side effects expected by parent callables.

# _attach_rule_metadata_keys

## Internal helper
Internal helper. Do not call directly from notebooks unless extending FabricOps.

## Purpose
Supports callable orchestration internals.

## Used by callable functions
- `fabricops_kit.data_quality.get_dq_review_results`

## Used by internal helpers
- None

## Debug relevance
Inspect this helper when parent callable outputs are malformed, missing evidence, or failing validation.

## Safe change guidance
Preserve helper contract, return shape, and side effects expected by parent callables.

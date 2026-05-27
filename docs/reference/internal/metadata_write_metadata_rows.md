# write_metadata_rows

## Internal helper
Internal helper. Do not call directly from notebooks unless extending FabricOps.

## Purpose
Supports callable orchestration internals.

## Used by callable functions
- `fabricops_kit.metadata.register_current_notebook`

## Used by internal helpers
- `fabricops_kit.metadata.write_column_business_context`
- `fabricops_kit.metadata.write_column_governance_context`

## Debug relevance
Inspect this helper when parent callable outputs are malformed, missing evidence, or failing validation.

## Safe change guidance
Preserve helper contract, return shape, and side effects expected by parent callables.

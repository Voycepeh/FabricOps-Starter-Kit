# default_schema_drift_policy

## Internal helper
Internal helper. Do not call directly from notebooks unless extending FabricOps.

## Purpose
Supports callable orchestration internals.

## Used by callable functions
- `fabricops_kit.drift.check_schema_drift`

## Used by internal helpers
- `fabricops_kit.drift.compare_schema_snapshots`

## Debug relevance
Inspect this helper when parent callable outputs are malformed, missing evidence, or failing validation.

## Safe change guidance
Preserve helper contract, return shape, and side effects expected by parent callables.

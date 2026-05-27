# _utc_now_iso

## Internal helper
Internal helper. Do not call directly from notebooks unless extending FabricOps.

## Purpose
Supports callable orchestration internals.

## Used by callable functions
- None

## Used by internal helpers
- `fabricops_kit.drift.build_and_write_partition_snapshot`
- `fabricops_kit.drift.build_and_write_schema_snapshot`
- `fabricops_kit.drift.build_drift_evidence_record`

## Debug relevance
Inspect this helper when parent callable outputs are malformed, missing evidence, or failing validation.

## Safe change guidance
Preserve helper contract, return shape, and side effects expected by parent callables.

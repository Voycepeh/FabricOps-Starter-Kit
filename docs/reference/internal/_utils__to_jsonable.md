# _to_jsonable

## Internal helper
Internal helper. Do not call directly from notebooks unless extending FabricOps.

## Purpose
Supports callable orchestration internals.

## Used by callable functions
- None

## Used by internal helpers
- `fabricops_kit._utils._to_jsonable`
- `fabricops_kit.drift._build_pandas_partition_snapshot`
- `fabricops_kit.drift._build_spark_partition_snapshot`
- `fabricops_kit.drift._json_dumps`
- `fabricops_kit.drift.build_incremental_safety_records`
- `fabricops_kit.drift.compare_partition_snapshots`

## Debug relevance
Inspect this helper when parent callable outputs are malformed, missing evidence, or failing validation.

## Safe change guidance
Preserve helper contract, return shape, and side effects expected by parent callables.

# _convert_single_parquet_ns_to_us

## Internal helper
Internal helper. Do not call directly from notebooks unless extending FabricOps.

## Purpose
Supports callable orchestration internals.

## Used by callable functions
- `fabricops_kit.fabric_input_output.read_lakehouse_parquet`

## Used by internal helpers
- None

## Debug relevance
Inspect this helper when parent callable outputs are malformed, missing evidence, or failing validation.

## Safe change guidance
Preserve helper contract, return shape, and side effects expected by parent callables.

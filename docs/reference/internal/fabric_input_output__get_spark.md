# _get_spark

## Internal helper
Internal helper. Do not call directly from notebooks unless extending FabricOps.

## Purpose
Supports callable orchestration internals.

## Used by callable functions
- `fabricops_kit.fabric_input_output.read_lakehouse_csv`
- `fabricops_kit.fabric_input_output.read_lakehouse_excel`
- `fabricops_kit.fabric_input_output.read_lakehouse_parquet`
- `fabricops_kit.fabric_input_output.read_lakehouse_table`
- `fabricops_kit.fabric_input_output.read_warehouse_table`

## Used by internal helpers
- `fabricops_kit.fabric_input_output.seed_minimal_sample_source_table`

## Debug relevance
Inspect this helper when parent callable outputs are malformed, missing evidence, or failing validation.

## Safe change guidance
Preserve helper contract, return shape, and side effects expected by parent callables.

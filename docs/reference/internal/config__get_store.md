# _get_store

## Internal helper
Internal helper. Do not call directly from notebooks unless extending FabricOps.

## Purpose
Supports callable orchestration internals.

## Used by callable functions
- `fabricops_kit.config.setup_notebook`
- `fabricops_kit.fabric_input_output.read_lakehouse_csv`
- `fabricops_kit.fabric_input_output.read_lakehouse_excel`
- `fabricops_kit.fabric_input_output.read_lakehouse_parquet`
- `fabricops_kit.fabric_input_output.read_lakehouse_table`
- `fabricops_kit.fabric_input_output.read_warehouse_table`
- `fabricops_kit.fabric_input_output.write_lakehouse_table`
- `fabricops_kit.fabric_input_output.write_warehouse_table`

## Used by internal helpers
- `fabricops_kit.config._bootstrap_fabric_env`
- `fabricops_kit.config._run_config_smoke_tests`

## Debug relevance
Inspect this helper when parent callable outputs are malformed, missing evidence, or failing validation.

## Safe change guidance
Preserve helper contract, return shape, and side effects expected by parent callables.

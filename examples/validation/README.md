# Fabric runtime validation examples

Fabric runtime validation notebooks now live under `examples/notebooks` so they can be imported alongside the other runnable example notebooks.

## DQ rule smoke test

Use `examples/notebooks/98_dq_rule_smoke_test.ipynb` as a one time smoke test after `00_env_config` is working and after the metadata lakehouse target can read and write FabricOps metadata tables.

The notebook creates sample Spark data with intentional valid and invalid rows, seeds approved active smoke test rules into `METADATA_DQ_RULES`, and runs `enforce_dq_rules` against that sample data. It validates that DQ rules are correctly read from `METADATA_DQ_RULES` and enforced by `enforce_dq_rules`.

This notebook is **not** part of the production workflow and is not a reusable starter kit workflow template. It uses stable smoke test dataset and table names so reruns remain scoped to validation metadata and do not affect normal project tables.

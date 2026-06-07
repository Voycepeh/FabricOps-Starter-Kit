# setup_metadata_tables

**Module:** `config`  
**Classification:** Callable

## Status

Public callable helper intended for notebook authors.

## When to use this

Use after setup_notebook in 00_env_config to create or validate the FabricOps metadata tables required by agreement, profiling, lineage, drift, and governance workflows.

## When not to use this

Do not use for writing business data or pipeline target tables; use write_lakehouse_table or write_warehouse_table for data outputs.

## Quick example

setup_metadata_tables(CONFIG, env="Sandbox", spark_session=spark)

## Signature

```python
def setup_metadata_tables(*, spark: Any, config: FrameworkConfig | dict[str, Any], env: str, require_active_steward: bool=False) -> dict[str, Any]
```

## Parameters

config, env, optional spark_session, and mode/check options used to prepare metadata storage through configured metadata routing.

## Returns

Setup result describing metadata table creation or validation status.

## Raises

Raises configuration, Spark, or storage errors when metadata routing or table preparation fails.

## Side effects

Creates or validates FabricOps metadata tables in the configured metadata lakehouse target.

## FabricOps context

Requires the metadata target from 00_env_config; metadata tables must be routed through CONFIG.path_config paths for the selected env.

## AI implementation contract

- **required_context:** Requires the metadata target from 00_env_config; metadata tables must be routed through CONFIG.path_config paths for the selected env.
- **inputs:** config, env, optional spark_session, and mode/check options used to prepare metadata storage through configured metadata routing.
- **output:** Setup result describing metadata table creation or validation status.
- **side_effects:** Creates or validates FabricOps metadata tables in the configured metadata lakehouse target.
- **failure_modes:** Raises configuration, Spark, or storage errors when metadata routing or table preparation fails.
- **verification:** Verify metadata setup completes before recommending agreement, profiling, lineage, drift, or governance workflows that persist evidence.

## Related functions

- <a href="../setup_notebook/"><code>fabricops_kit.config.setup_notebook</code></a>
- <a href="../record_table_governance/"><code>fabricops_kit.governance_review.record_table_governance</code></a>

## Source and tests

- Source file path: `src/fabricops_kit/config.py`
- Source reference: <a href="../../api/modules/config/#setup_metadata_tables">Module source anchor</a>
- Tests: Not documented yet

## Function manifest

- Fully qualified function name: `fabricops_kit.config.setup_metadata_tables`
- Short name: `setup_metadata_tables`
- Module: `config`
- Classification: Callable
- Related module: `config`
- Inbound references count: 0
- Outbound references count: 4

## Outbound references
- <a href="../internal/data_agreement__setup_data_agreement_tables/"><code>fabricops_kit.data_agreement._setup_data_agreement_tables</code></a>
- <a href="../internal/governance_review__setup_governance_metadata_tables/"><code>fabricops_kit.governance_review._setup_governance_metadata_tables</code></a>
- <a href="../internal/metadata__setup_notebook_registry_table/"><code>fabricops_kit.metadata._setup_notebook_registry_table</code></a>

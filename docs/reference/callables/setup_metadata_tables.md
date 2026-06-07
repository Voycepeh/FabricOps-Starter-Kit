# setup_metadata_tables

**Module:** `config`  
**Classification:** Callable

## Status

Public callable helper intended for notebook authors.

## When to use this

Create or validate all FabricOps metadata tables through one setup action.

## When not to use this

Not documented yet

## Quick example

Not documented yet

## Signature

```python
def setup_metadata_tables(*, spark: Any, config: FrameworkConfig | dict[str, Any], env: str, require_active_steward: bool=False) -> dict[str, Any]
```

## Parameters

spark : pyspark.sql.SparkSession
    Fabric Spark session used by the table setup helpers.
config : FrameworkConfig or dict
    Shared ``00_env_config`` configuration containing the metadata target.
env : str
    Environment key to prepare.
require_active_steward : bool, default=False
    Forwarded to the agreement metadata setup to optionally require an
    active steward before returning success.

## Returns

dict[str, Any]
    Combined setup summary keyed by ``data_agreement``,
    ``notebook_registry``, and ``governance``.

## Raises

Not documented yet

## Side effects

Not documented yet

## FabricOps context

Starter template: `00_env_config`; segment: `Environment bootstrap`.

## AI implementation contract

Not documented yet

## Related functions

- <a href="../internal/data_agreement__setup_data_agreement_tables/"><code>fabricops_kit.data_agreement._setup_data_agreement_tables</code></a>
- `fabricops_kit.data_agreement.get`
- <a href="../internal/governance_review__setup_governance_metadata_tables/"><code>fabricops_kit.governance_review._setup_governance_metadata_tables</code></a>
- <a href="../internal/metadata__setup_notebook_registry_table/"><code>fabricops_kit.metadata._setup_notebook_registry_table</code></a>

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

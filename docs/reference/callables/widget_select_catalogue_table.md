# widget_select_catalogue_table

**Module:** `governance_review`  
**Classification:** Callable

## Status

Public callable helper intended for notebook authors.

## When to use this

Render a searchable selector for latest successful catalogue profiles.

## When not to use this

Not documented yet

## Quick example

Not documented yet

## Signature

```python
def widget_select_catalogue_table(config: Any, env: str, *, spark_session: Any)
```

## Parameters

config : FrameworkConfig or dict
    Runtime config containing the metadata lakehouse route.
env : str
    Environment used to read ``METADATA_DATA_CATALOGUE``.
spark_session : pyspark.sql.SparkSession
    Spark session used for the catalogue read.

## Returns

ipywidgets.Combobox
    Searchable selector whose value stores stable JSON identity.

## Raises

Not documented yet

## Side effects

Not documented yet

## FabricOps context

Starter template: `03_review`; segment: `Governance review`.

## AI implementation contract

- **required_context:** Starter template: `03_review`; segment: `Governance review`.
- **inputs:** config : FrameworkConfig or dict
    Runtime config containing the metadata lakehouse route.
env : str
    Environment used to read ``METADATA_DATA_CATALOGUE``.
spark_session : pyspark.sql.SparkSession
    Spark session used for the catalogue read.
- **output:** ipywidgets.Combobox
    Searchable selector whose value stores stable JSON identity.
- **side_effects:** Not documented yet
- **failure_modes:** Not documented yet
- **verification:** Not documented yet

## Related functions

- <a href="../read_lakehouse_table/"><code>fabricops_kit.fabric_input_output.read_lakehouse_table</code></a>
- <a href="../internal/governance_review__catalogue_table_options/"><code>fabricops_kit.governance_review._catalogue_table_options</code></a>
- <a href="../internal/governance_review__coerce_rows/"><code>fabricops_kit.governance_review._coerce_rows</code></a>

## Source and tests

- Source file path: `src/fabricops_kit/governance_review.py`
- Source reference: <a href="../../api/modules/governance_review/#widget_select_catalogue_table">Module source anchor</a>
- Tests: Not documented yet

## Function manifest

- Fully qualified function name: `fabricops_kit.governance_review.widget_select_catalogue_table`
- Short name: `widget_select_catalogue_table`
- Module: `governance_review`
- Classification: Callable
- Related module: `governance_review`
- Inbound references count: 0
- Outbound references count: 3

## Outbound references
- <a href="../read_lakehouse_table/"><code>fabricops_kit.fabric_input_output.read_lakehouse_table</code></a>
- <a href="../internal/governance_review__catalogue_table_options/"><code>fabricops_kit.governance_review._catalogue_table_options</code></a>
- <a href="../internal/governance_review__coerce_rows/"><code>fabricops_kit.governance_review._coerce_rows</code></a>

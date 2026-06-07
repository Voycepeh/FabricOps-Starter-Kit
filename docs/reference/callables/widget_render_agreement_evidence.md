# widget_render_agreement_evidence

**Module:** `data_agreement`  
**Classification:** Callable

## Status

Public callable helper intended for notebook authors.

## When to use this

Render the standalone agreement-evidence widget.

## When not to use this

Not documented yet

## Quick example

Not documented yet

## Signature

```python
def widget_render_agreement_evidence(config: Any, env_name: str, *, spark: Any) -> dict[str, Any]
```

## Parameters

config : FrameworkConfig or dict
    Configuration containing agreement metadata routing and evidence table
    settings.
env_name : str
    Environment key configured by ``00_env_config``.
spark : pyspark.sql.SparkSession
    Fabric Spark session used for metadata reads, file writes, and
    append-only evidence metadata writes.

## Returns

dict[str, Any]
    Rendered controls for selecting an agreement version, pasting
    metadata lakehouse evidence file paths, refreshing agreement options,
    and saving evidence metadata rows.

## Raises

Not documented yet

## Side effects

Not documented yet

## FabricOps context

Starter template: `01_agreement`; segment: `Agreement intake`.

## AI implementation contract

Not documented yet

## Related functions

- <a href="../internal/data_agreement__render_agreement_evidence_widget/"><code>fabricops_kit.data_agreement._render_agreement_evidence_widget</code></a>

## Source and tests

- Source file path: `src/fabricops_kit/data_agreement.py`
- Source reference: <a href="../../api/modules/data_agreement/#widget_render_agreement_evidence">Module source anchor</a>
- Tests: Not documented yet

## Function manifest

- Fully qualified function name: `fabricops_kit.data_agreement.widget_render_agreement_evidence`
- Short name: `widget_render_agreement_evidence`
- Module: `data_agreement`
- Classification: Callable
- Related module: `data_agreement`
- Inbound references count: 0
- Outbound references count: 1

## Outbound references
- <a href="../internal/data_agreement__render_agreement_evidence_widget/"><code>fabricops_kit.data_agreement._render_agreement_evidence_widget</code></a>

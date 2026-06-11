# _runtime_audit_fields

**Module:** `pipeline`  
**Classification:** Internal

## Status

Internal helper used by the package implementation.

## Function type: Internal helper

Internal helper

## Direct use: No

Do not call this helper directly from notebooks; use the public callable helpers instead.

## Used by

- <a href="../write_catalogue_evidence/"><code>fabricops_kit.pipeline.write_catalogue_evidence</code></a>
- <a href="../write_pipeline_lineage/"><code>fabricops_kit.pipeline.write_pipeline_lineage</code></a>

## Purpose

No summary available.

## Signature if available

```python
def _runtime_audit_fields(config: Any, env: str) -> dict[str, str]
```

## Side effects

Not documented yet

## Maintainer notes

Maintain this helper through the owning implementation module and keep generated references in sync.

## AI implementation contract

Use internal pages only for package maintenance. Prefer public callable pages when authoring notebooks.

## Function manifest

- Fully qualified function name: `fabricops_kit.pipeline._runtime_audit_fields`
- Short name: `_runtime_audit_fields`
- Module: `pipeline`
- Classification: Internal
- Related module: `pipeline`
- Source file path: `src/fabricops_kit/pipeline.py`
- Source reference: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/a212c94775e71b6e429e41b51fbc57ac733903cb/src/fabricops_kit/pipeline.py#L49-L60">View source on GitHub</a>
- Inbound references count: 2
- Outbound references count: 2

## Inbound references
- <a href="../write_catalogue_evidence/"><code>fabricops_kit.pipeline.write_catalogue_evidence</code></a>
- <a href="../write_pipeline_lineage/"><code>fabricops_kit.pipeline.write_pipeline_lineage</code></a>

## Outbound references
- <a href="../internal/metadata__build_runtime_audit_fields/"><code>fabricops_kit.metadata._build_runtime_audit_fields</code></a>
- <a href="../internal/pipeline__now_iso/"><code>fabricops_kit.pipeline._now_iso</code></a>

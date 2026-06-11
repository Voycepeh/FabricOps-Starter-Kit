# _build_guardrail_evidence_definitions

**Module:** `pipeline`
**Classification:** Internal

## Status

Internal helper used by the package implementation.

## Function type: Internal helper

Internal helper

## Direct use: No

Do not call this helper directly from notebooks; use the public callable helpers instead.

## Used by

- <a href="../run_table_guardrails/"><code>fabricops_kit.pipeline.run_table_guardrails</code></a>

## Purpose

Build catalogue evidence definitions for pipeline table guardrails.

## Signature if available

```python
def _build_guardrail_evidence_definitions(table_configs: list[Mapping[str, Any]]) -> dict[str, dict[str, Any]]
```

## Side effects

Not documented yet

## Maintainer notes

Maintain this helper through the owning implementation module and keep generated references in sync.

## AI implementation contract

Use internal pages only for package maintenance. Prefer public callable pages when authoring notebooks.

## Function manifest

- Fully qualified function name: `fabricops_kit.pipeline._build_guardrail_evidence_definitions`
- Short name: `_build_guardrail_evidence_definitions`
- Module: `pipeline`
- Classification: Internal
- Related module: `pipeline`
- Source file path: `src/fabricops_kit/pipeline.py`
- Source reference: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1bac7913a070db1a771a2991ff5421c37ffc9d94/src/fabricops_kit/pipeline.py#L228-L257">View source on GitHub</a>
- Inbound references count: 1
- Outbound references count: 2

## Inbound references
- <a href="../run_table_guardrails/"><code>fabricops_kit.pipeline.run_table_guardrails</code></a>

## Outbound references
- <a href="../internal/pipeline__table_key/"><code>fabricops_kit.pipeline._table_key</code></a>
- <a href="../internal/pipeline__table_name/"><code>fabricops_kit.pipeline._table_name</code></a>

# _schema_guardrail_rows

**Module:** `drift`  
**Classification:** Internal

## Status

Internal helper used by the package implementation.

## Function type: Internal helper

Internal helper

## Direct use: No

Do not call this helper directly from notebooks; use the public callable helpers instead.

## Used by

- <a href="../internal/drift__generate_schema_guardrail_config/"><code>fabricops_kit.drift._generate_schema_guardrail_config</code></a>

## Purpose

Return schema rows used by the public schema guardrail generator.

## Signature if available

```python
def _schema_guardrail_rows(dataframe, *, exclude_columns: list[str] | set[str] | tuple[str, ...] | None=None, sort_columns: bool=False) -> list[dict[str, str | bool | None]]
```

## Side effects

Not documented yet

## Maintainer notes

Maintain this helper through the owning implementation module and keep generated references in sync.

## AI implementation contract

Use internal pages only for package maintenance. Prefer public callable pages when authoring notebooks.

## Function manifest

- Fully qualified function name: `fabricops_kit.drift._schema_guardrail_rows`
- Short name: `_schema_guardrail_rows`
- Module: `drift`
- Classification: Internal
- Related module: `drift`
- Source file path: `src/fabricops_kit/drift.py`
- Source reference: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/3d2707796405a2e3e2f36d7a599be05589995508/src/fabricops_kit/drift.py#L106-L138">View source on GitHub</a>
- Inbound references count: 1
- Outbound references count: 2

## Inbound references
- <a href="../internal/drift__generate_schema_guardrail_config/"><code>fabricops_kit.drift._generate_schema_guardrail_config</code></a>

## Outbound references
- <a href="../internal/drift__actual_schema/"><code>fabricops_kit.drift._actual_schema</code></a>
- <a href="../internal/drift__normalize_datatype/"><code>fabricops_kit.drift._normalize_datatype</code></a>

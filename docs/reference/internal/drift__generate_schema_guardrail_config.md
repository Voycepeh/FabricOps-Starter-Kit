# _generate_schema_guardrail_config

**Module:** `drift`  
**Classification:** Internal

## Status

Internal helper used by the package implementation.

## Function type: Internal helper

Internal helper

## Direct use: No

Do not call this helper directly from notebooks; use the public callable helpers instead.

## Used by

Not documented yet

## Purpose

Generate internal starter schema guardrail config from a DataFrame schema.

## Signature if available

```python
def _generate_schema_guardrail_config(dataframe, *, exclude_columns: list[str] | set[str] | tuple[str, ...] | None=None, sort_columns: bool=False, output_format: str='dict')
```

## Side effects

Not documented yet

## Maintainer notes

Maintain this helper through the owning implementation module and keep generated references in sync.

## AI implementation contract

Use internal pages only for package maintenance. Prefer public callable pages when authoring notebooks.

## Function manifest

- Fully qualified function name: `fabricops_kit.drift._generate_schema_guardrail_config`
- Short name: `_generate_schema_guardrail_config`
- Module: `drift`
- Classification: Internal
- Related module: `drift`
- Source file path: `src/fabricops_kit/drift.py`
- Source reference: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/3d2707796405a2e3e2f36d7a599be05589995508/src/fabricops_kit/drift.py#L141-L198">View source on GitHub</a>
- Inbound references count: 0
- Outbound references count: 2

## Outbound references
- <a href="../internal/drift__schema_guardrail_rows/"><code>fabricops_kit.drift._schema_guardrail_rows</code></a>

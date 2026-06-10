# _flatten_chain

**Module:** `data_lineage`  
**Classification:** Internal

## Status

Internal helper used by the package implementation.

## Function type: Internal helper

Internal helper

## Direct use: No

Do not call this helper directly from notebooks; use the public callable helpers instead.

## Used by

- <a href="../internal/data_lineage__scan_notebook_lineage/"><code>fabricops_kit.data_lineage._scan_notebook_lineage</code></a>

## Purpose

No summary available.

## Signature if available

```python
def _flatten_chain(node: ast.AST) -> tuple[str | None, list[str]]
```

## Side effects

Not documented yet

## Maintainer notes

Maintain this helper through the owning implementation module and keep generated references in sync.

## AI implementation contract

Use internal pages only for package maintenance. Prefer public callable pages when authoring notebooks.

## Function manifest

- Fully qualified function name: `fabricops_kit.data_lineage._flatten_chain`
- Short name: `_flatten_chain`
- Module: `data_lineage`
- Classification: Internal
- Related module: `data_lineage`
- Source file path: `src/fabricops_kit/data_lineage.py`
- Source reference: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/6d8de4b3e35399458b9ee2a79568a6d6f1831a4e/src/fabricops_kit/data_lineage.py#L13-L18">View source on GitHub</a>
- Inbound references count: 1
- Outbound references count: 0

## Inbound references
- <a href="../internal/data_lineage__scan_notebook_lineage/"><code>fabricops_kit.data_lineage._scan_notebook_lineage</code></a>

# _scan_notebook_lineage

**Module:** `data_lineage`  
**Classification:** Internal

## Status

Internal helper used by the package implementation.

## Function type: Internal helper

Internal helper

## Direct use: No

Do not call this helper directly from notebooks; use the public callable helpers instead.

## Used by

- <a href="../internal/data_lineage__scan_notebook_cells/"><code>fabricops_kit.data_lineage._scan_notebook_cells</code></a>

## Purpose

Extract deterministic lineage steps from notebook code using AST parsing.

## Signature if available

```python
def _scan_notebook_lineage(code: str) -> list[dict[str, Any]]
```

## Side effects

Not documented yet

## Maintainer notes

Maintain this helper through the owning implementation module and keep generated references in sync.

## AI implementation contract

Use internal pages only for package maintenance. Prefer public callable pages when authoring notebooks.

## Function manifest

- Fully qualified function name: `fabricops_kit.data_lineage._scan_notebook_lineage`
- Short name: `_scan_notebook_lineage`
- Module: `data_lineage`
- Classification: Internal
- Related module: `data_lineage`
- Source file path: `src/fabricops_kit/data_lineage.py`
- Source reference: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/b37a3d3a2b947b2e265229d7ea688a0bac6a5396/src/fabricops_kit/data_lineage.py#L36-L85">View source on GitHub</a>
- Inbound references count: 1
- Outbound references count: 2

## Inbound references
- <a href="../internal/data_lineage__scan_notebook_cells/"><code>fabricops_kit.data_lineage._scan_notebook_cells</code></a>

## Outbound references
- <a href="../internal/data_lineage__flatten_chain/"><code>fabricops_kit.data_lineage._flatten_chain</code></a>
- <a href="../internal/data_lineage__resolve_write_target/"><code>fabricops_kit.data_lineage._resolve_write_target</code></a>

# _scan_notebook_cells

**Module:** `data_lineage`
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

Scan multiple notebook cells and append cell references to lineage steps.

## Signature if available

```python
def _scan_notebook_cells(cells: list[str]) -> list[dict[str, Any]]
```

## Side effects

Not documented yet

## Maintainer notes

Maintain this helper through the owning implementation module and keep generated references in sync.

## AI implementation contract

Use internal pages only for package maintenance. Prefer public callable pages when authoring notebooks.

## Function manifest

- Fully qualified function name: `fabricops_kit.data_lineage._scan_notebook_cells`
- Short name: `_scan_notebook_cells`
- Module: `data_lineage`
- Classification: Internal
- Related module: `data_lineage`
- Source file path: `src/fabricops_kit/data_lineage.py`
- Source reference: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1bac7913a070db1a771a2991ff5421c37ffc9d94/src/fabricops_kit/data_lineage.py#L89-L107">View source on GitHub</a>
- Inbound references count: 0
- Outbound references count: 1

## Outbound references
- <a href="../internal/data_lineage__scan_notebook_lineage/"><code>fabricops_kit.data_lineage._scan_notebook_lineage</code></a>

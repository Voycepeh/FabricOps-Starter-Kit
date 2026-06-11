# _lakehouse_file_path

**Module:** `fabric_input_output`  
**Classification:** Internal

## Status

Internal helper used by the package implementation.

## Function type: Internal helper

Internal helper

## Direct use: No

Do not call this helper directly from notebooks; use the public callable helpers instead.

## Used by

- <a href="../read_lakehouse_csv/"><code>fabricops_kit.fabric_input_output.read_lakehouse_csv</code></a>
- <a href="../read_lakehouse_excel/"><code>fabricops_kit.fabric_input_output.read_lakehouse_excel</code></a>
- <a href="../read_lakehouse_parquet/"><code>fabricops_kit.fabric_input_output.read_lakehouse_parquet</code></a>

## Purpose

Return an ABFSS path under a configured lakehouse Files area.

## Signature if available

```python
def _lakehouse_file_path(store, env: str, target: str, relative_path: str) -> str
```

## Side effects

Not documented yet

## Maintainer notes

Maintain this helper through the owning implementation module and keep generated references in sync.

## AI implementation contract

Use internal pages only for package maintenance. Prefer public callable pages when authoring notebooks.

## Function manifest

- Fully qualified function name: `fabricops_kit.fabric_input_output._lakehouse_file_path`
- Short name: `_lakehouse_file_path`
- Module: `fabric_input_output`
- Classification: Internal
- Related module: `fabric_input_output`
- Source file path: `src/fabricops_kit/fabric_input_output.py`
- Source reference: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/cb8dad0bc076c72220f65712e627dcc0b38043e0/src/fabricops_kit/fabric_input_output.py#L120-L130">View source on GitHub</a>
- Inbound references count: 3
- Outbound references count: 0

## Inbound references
- <a href="../read_lakehouse_csv/"><code>fabricops_kit.fabric_input_output.read_lakehouse_csv</code></a>
- <a href="../read_lakehouse_excel/"><code>fabricops_kit.fabric_input_output.read_lakehouse_excel</code></a>
- <a href="../read_lakehouse_parquet/"><code>fabricops_kit.fabric_input_output.read_lakehouse_parquet</code></a>

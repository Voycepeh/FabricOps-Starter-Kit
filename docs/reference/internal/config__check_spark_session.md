# _check_spark_session

**Module:** `config`  
**Classification:** Internal

## Status

Internal helper used by the package implementation.

## Function type: Internal helper

Internal helper

## Direct use: No

Do not call this helper directly from notebooks; use the public callable helpers instead.

## Used by

- <a href="../internal/config__run_config_smoke_tests/"><code>fabricops_kit.config._run_config_smoke_tests</code></a>

## Purpose

Check whether a Spark session is available.

## Signature if available

```python
def _check_spark_session() -> tuple[bool, str]
```

## Side effects

Not documented yet

## Maintainer notes

Maintain this helper through the owning implementation module and keep generated references in sync.

## AI implementation contract

Use internal pages only for package maintenance. Prefer public callable pages when authoring notebooks.

## Function manifest

- Fully qualified function name: `fabricops_kit.config._check_spark_session`
- Short name: `_check_spark_session`
- Module: `config`
- Classification: Internal
- Related module: `config`
- Source file path: `src/fabricops_kit/config.py`
- Source reference: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/cb8dad0bc076c72220f65712e627dcc0b38043e0/src/fabricops_kit/config.py#L873-L878">View source on GitHub</a>
- Inbound references count: 1
- Outbound references count: 0

## Inbound references
- <a href="../internal/config__run_config_smoke_tests/"><code>fabricops_kit.config._run_config_smoke_tests</code></a>

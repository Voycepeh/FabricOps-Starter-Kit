# _validate_framework_config

**Module:** `config`  
**Classification:** Internal

## Status

Internal helper used by the package implementation.

## Function type: Internal helper

Internal helper

## Direct use: No

Do not call this helper directly from notebooks; use the public callable helpers instead.

## Used by

- <a href="../setup_notebook/"><code>fabricops_kit.config.setup_notebook</code></a>

## Purpose

Validate and normalize framework configuration input.

## Signature if available

```python
def _validate_framework_config(config: FrameworkConfig | dict[str, Any]) -> FrameworkConfig
```

## Side effects

Not documented yet

## Maintainer notes

Maintain this helper through the owning implementation module and keep generated references in sync.

## AI implementation contract

Use internal pages only for package maintenance. Prefer public callable pages when authoring notebooks.

## Function manifest

- Fully qualified function name: `fabricops_kit.config._validate_framework_config`
- Short name: `_validate_framework_config`
- Module: `config`
- Classification: Internal
- Related module: `config`
- Source file path: `src/fabricops_kit/config.py`
- Source reference: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/6d8de4b3e35399458b9ee2a79568a6d6f1831a4e/src/fabricops_kit/config.py#L470-L545">View source on GitHub</a>
- Inbound references count: 1
- Outbound references count: 2

## Inbound references
- <a href="../setup_notebook/"><code>fabricops_kit.config.setup_notebook</code></a>

## Outbound references
- <a href="../internal/config_FrameworkConfig/"><code>fabricops_kit.config.FrameworkConfig</code></a>

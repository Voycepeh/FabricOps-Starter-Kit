# _latest_catalogue_behavior_profile_row

**Module:** `guardrails`
**Classification:** Internal

## Status

Internal helper used by the package implementation.

## Function type: Internal helper

Internal helper

## Direct use: No

Do not call this helper directly from notebooks; use the public callable helpers instead.

## Used by

- <a href="../enforce_profile_behavior/"><code>fabricops_kit.guardrails.enforce_profile_behavior</code></a>

## Purpose

No summary available.

## Signature if available

```python
def _latest_catalogue_behavior_profile_row(catalogue_df, *, dataset_name: str, table_name: str, profile_stage: str, load_behavior: str, watermark_column: str | None=None, exclude_run_id: str | None=None) -> dict | None
```

## Side effects

Not documented yet

## Maintainer notes

Maintain this helper through the owning implementation module and keep generated references in sync.

## AI implementation contract

Use internal pages only for package maintenance. Prefer public callable pages when authoring notebooks.

## Function manifest

- Fully qualified function name: `fabricops_kit.guardrails._latest_catalogue_behavior_profile_row`
- Short name: `_latest_catalogue_behavior_profile_row`
- Module: `guardrails`
- Classification: Internal
- Related module: `guardrails`
- Source file path: `src/fabricops_kit/guardrails.py`
- Source reference: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/a80b5a6ddb4de14056095d4da916cd452e478ff8/src/fabricops_kit/guardrails.py#L521-L630">View source on GitHub</a>
- Inbound references count: 1
- Outbound references count: 4

## Inbound references
- <a href="../enforce_profile_behavior/"><code>fabricops_kit.guardrails.enforce_profile_behavior</code></a>

## Outbound references
- <a href="../internal/guardrails__catalogue_value/"><code>fabricops_kit.guardrails._catalogue_value</code></a>
- <a href="../internal/guardrails__is_missing_table_error/"><code>fabricops_kit.guardrails._is_missing_table_error</code></a>
- <a href="../internal/guardrails__row_to_dict/"><code>fabricops_kit.guardrails._row_to_dict</code></a>
- <a href="../internal/guardrails__string_value/"><code>fabricops_kit.guardrails._string_value</code></a>

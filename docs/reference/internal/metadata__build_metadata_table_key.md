# _build_metadata_table_key

**Module:** `metadata`  
**Classification:** Internal

## Status

Internal helper used by the package implementation.

## Function type: Internal helper

Internal helper

## Direct use: No

Do not call this helper directly from notebooks; use the public callable helpers instead.

## Used by

- <a href="../internal/governance_review__approved_column_identity/"><code>fabricops_kit.governance_review._approved_column_identity</code></a>
- <a href="../internal/governance_review__catalogue_table_options/"><code>fabricops_kit.governance_review._catalogue_table_options</code></a>
- <a href="../internal/governance_review__review_governance_evidence/"><code>fabricops_kit.governance_review._review_governance_evidence</code></a>
- <a href="../load_catalogue_profile_rows/"><code>fabricops_kit.governance_review.load_catalogue_profile_rows</code></a>
- <a href="../write_catalogue_evidence/"><code>fabricops_kit.pipeline.write_catalogue_evidence</code></a>
- <a href="../write_pipeline_lineage/"><code>fabricops_kit.pipeline.write_pipeline_lineage</code></a>

## Purpose

No summary available.

## Signature if available

```python
def _build_metadata_table_key(environment_name, dataset_name, table_name) -> str
```

## Side effects

Not documented yet

## Maintainer notes

Maintain this helper through the owning implementation module and keep generated references in sync.

## AI implementation contract

Use internal pages only for package maintenance. Prefer public callable pages when authoring notebooks.

## Function manifest

- Fully qualified function name: `fabricops_kit.metadata._build_metadata_table_key`
- Short name: `_build_metadata_table_key`
- Module: `metadata`
- Classification: Internal
- Related module: `metadata`
- Source file path: `src/fabricops_kit/metadata.py`
- Source reference: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/6d8de4b3e35399458b9ee2a79568a6d6f1831a4e/src/fabricops_kit/metadata.py#L148-L149">View source on GitHub</a>
- Inbound references count: 6
- Outbound references count: 1

## Inbound references
- <a href="../internal/governance_review__approved_column_identity/"><code>fabricops_kit.governance_review._approved_column_identity</code></a>
- <a href="../internal/governance_review__catalogue_table_options/"><code>fabricops_kit.governance_review._catalogue_table_options</code></a>
- <a href="../internal/governance_review__review_governance_evidence/"><code>fabricops_kit.governance_review._review_governance_evidence</code></a>
- <a href="../load_catalogue_profile_rows/"><code>fabricops_kit.governance_review.load_catalogue_profile_rows</code></a>
- <a href="../write_catalogue_evidence/"><code>fabricops_kit.pipeline.write_catalogue_evidence</code></a>
- <a href="../write_pipeline_lineage/"><code>fabricops_kit.pipeline.write_pipeline_lineage</code></a>

## Outbound references
- <a href="../internal/metadata__stable_metadata_key/"><code>fabricops_kit.metadata._stable_metadata_key</code></a>

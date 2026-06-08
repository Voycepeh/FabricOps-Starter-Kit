# _write_catalogue_evidence

**Module:** `pipeline`  
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

Enrich profile rows with guardrail context and write catalogue evidence.

## Signature if available

```python
def _write_catalogue_evidence(profiles: Mapping[str, Any], dataset_definitions: Mapping[str, Mapping[str, Any]], *, config: Any, env: str, run_id: str, agreement_id: str='', agreement_contract_version: str='', notebook_registry_id: str='', notebook_id: str='', pipeline_name: str='', schema_results: Mapping[str, Mapping[str, Any]] | None=None, drift_results: Mapping[str, Mapping[str, Any]] | None=None, dq_results: Mapping[str, Mapping[str, Any]] | None=None, metadata_table: str=CATALOGUE_TABLE, mode: str='append') -> dict[str, str]
```

## Side effects

Not documented yet

## Maintainer notes

Maintain this helper through the owning implementation module and keep generated references in sync.

## AI implementation contract

Use internal pages only for package maintenance. Prefer public callable pages when authoring notebooks.

## Function manifest

- Fully qualified function name: `fabricops_kit.pipeline._write_catalogue_evidence`
- Short name: `_write_catalogue_evidence`
- Module: `pipeline`
- Classification: Internal
- Related module: `pipeline`
- Source file path: `src/fabricops_kit/pipeline.py`
- Source reference: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/692f3e5f0ea66047651f28067ac9b1d375c9afc8/src/fabricops_kit/pipeline.py#L70-L178">View source on GitHub</a>
- Inbound references count: 0
- Outbound references count: 5

## Outbound references
- <a href="../write_lakehouse_table/"><code>fabricops_kit.fabric_input_output.write_lakehouse_table</code></a>
- <a href="../internal/metadata__build_metadata_table_key/"><code>fabricops_kit.metadata._build_metadata_table_key</code></a>
- <a href="../internal/pipeline__definition_name/"><code>fabricops_kit.pipeline._definition_name</code></a>
- <a href="../internal/pipeline__dq_summary_fields/"><code>fabricops_kit.pipeline._dq_summary_fields</code></a>
- <a href="../internal/pipeline__runtime_audit_fields/"><code>fabricops_kit.pipeline._runtime_audit_fields</code></a>

# _register_current_notebook

**Module:** `metadata`  
**Classification:** Internal

## Status

Internal helper used by the package implementation.

## Function type: Internal helper

Internal helper

## Direct use: No

Do not call this helper directly from notebooks; use the public callable helpers instead.

## Used by

- <a href="../widget_select_agreement/"><code>fabricops_kit.data_agreement.widget_select_agreement</code></a>

## Purpose

Append a runtime notebook registration row.

## Signature if available

```python
def _register_current_notebook(spark, agreement_id=None, notebook_type=None, environment_name=None, dataset_name=None, table_name=None, topic=None, pipeline_name=None, contract_version=None, registration_role='primary', registration_status='active', registration_id=None, superseded_at=None, superseded_by_registration_id=None, metadata_table=NOTEBOOK_REGISTRY_TABLE, *, config: Any=None, env: str | None=None)
```

## Side effects

Not documented yet

## Maintainer notes

Maintain this helper through the owning implementation module and keep generated references in sync.

## AI implementation contract

Use internal pages only for package maintenance. Prefer public callable pages when authoring notebooks.

## Function manifest

- Fully qualified function name: `fabricops_kit.metadata._register_current_notebook`
- Short name: `_register_current_notebook`
- Module: `metadata`
- Classification: Internal
- Related module: `metadata`
- Source file path: `src/fabricops_kit/metadata.py`
- Source reference: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/7671b3d58873b7627843d2a35ac9cb4dae15eb9a/src/fabricops_kit/metadata.py#L291-L404">View source on GitHub</a>
- Inbound references count: 1
- Outbound references count: 6

## Inbound references
- <a href="../widget_select_agreement/"><code>fabricops_kit.data_agreement.widget_select_agreement</code></a>

## Outbound references
- <a href="../write_lakehouse_table/"><code>fabricops_kit.fabric_input_output.write_lakehouse_table</code></a>
- <a href="../internal/metadata__context_get/"><code>fabricops_kit.metadata._context_get</code></a>
- <a href="../internal/metadata__notebook_registration_key/"><code>fabricops_kit.metadata._notebook_registration_key</code></a>
- <a href="../internal/metadata__rows_for_spark/"><code>fabricops_kit.metadata._rows_for_spark</code></a>
- <a href="../internal/metadata__runtime_context/"><code>fabricops_kit.metadata._runtime_context</code></a>
- <a href="../internal/metadata__safe_str/"><code>fabricops_kit.metadata._safe_str</code></a>

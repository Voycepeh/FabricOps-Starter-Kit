# prepare_pipeline_table_configs

??? info "Downstream callables: 4"

    Dependency data is generated from the callable architecture inventory.

    <div class="reference-call-tree" role="tree" data-callable-architecture-flow="true">
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix"></span><span class="reference-call-tree-source">[pipeline/prepare_pipeline_table_configs.py]</span> <span class="reference-call-tree-type">[public callable]</span> <code>prepare_pipeline_table_configs(...)</code></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">└── </span><span class="reference-call-tree-source">[pipeline/shared.py]</span> <span class="reference-call-tree-type">[private helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline/shared.py#L735-L835" class="reference-call-tree-callable"><code>_prepare_pipeline_table_configs_workflow(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    └── </span><span class="reference-call-tree-source">[config/shared.py]</span> <span class="reference-call-tree-type">[shared helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/shared.py#L164-L172" class="reference-call-tree-callable"><code>get_current_audit_timestamp(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">        └── </span><span class="reference-call-tree-source">[config/shared.py]</span> <span class="reference-call-tree-type">[shared helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/shared.py#L156-L161" class="reference-call-tree-callable"><code>get_audit_timezone(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">            └── </span><span class="reference-call-tree-source">[config/shared.py]</span> <span class="reference-call-tree-type">[private helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/shared.py#L116-L148" class="reference-call-tree-callable"><code>_validate_audit_timezone(...)</code></a></div>
    </div>

Prepare source or target table configs for 02_pipeline.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/pipeline/prepare_pipeline_table_configs.py:10`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline/prepare_pipeline_table_configs.py#L10-L25">View on GitHub</a>
</div>

<p class="reference-catalogue-item-meta reference-catalogue-item-badges">
<span class="reference-chip">Public Starter Kit function</span>
<span class="reference-chip">02_pipeline</span>
</p>

**Used in notebooks:** `02_pipeline`

## Usage guidance

### Use when

- Use before running table guardrails or writes when notebook-editable table configs need package defaults and derived keys.

### Do not use when

- Do not use for ad hoc reads or writes outside the pipeline table-config pattern.

### Additional context

Normalizes source and target table configuration dictionaries so pipeline guardrail, write, lineage, and evidence helpers receive consistent fields.


## Signature

<div class="reference-api-definition" markdown="1">

```python
def prepare_pipeline_table_configs(
    table_configs: list[dict[str, Any]],
    default_settings: Mapping[str, Any],
    table_role: str,
    run_id: str='',
    pipeline_name: str='',
) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
```

</div>

## Example usage

<div class="reference-example-usage" markdown="1">

```python
SOURCE_TABLES, SOURCE_CONFIG_BY_KEY = prepare_pipeline_table_configs(SOURCE_TABLES, {}, table_role="source")
```

</div>

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `table_configs` | `list[dict[str, Any]]` | Yes | Not documented yet |
| `default_settings` | `Mapping[str, Any]` | Yes | Not documented yet |
| `table_role` | `str` | Yes | Not documented yet |
| `run_id` | `str` | No | Not documented yet |
| `pipeline_name` | `str` | No | Not documented yet |

## Returns

Enriched table configs and a dictionary keyed by table key.

### Return interpretation

The returned configs are enriched copies keyed for downstream helpers. Confirm each table has the expected stage, key, and write settings.

## Raises / Errors

Not documented yet

### Common failure causes

- A table config is missing key or table_name fields.
- Stage or write settings are inconsistent.
- Source and target config shapes differ from expected dictionaries.
- Defaults in CONFIG do not match the notebook environment.

## See also

- [Notebook Templates Implementation Guide](../../notebook-templates-implementation-guide/index.md)
- [Pipeline Execution](../../notebook-templates-implementation-guide/pipeline-execution.md)

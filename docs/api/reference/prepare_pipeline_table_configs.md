# prepare_pipeline_table_configs

## Call-flow summary

- Downstream callables: 4
- Shared helpers: 2
- Private helpers: 2

<a class="reference-source-link" href="../../../assets/public-function-call-flows-dashboard.html?function=prepare_pipeline_table_configs">Open focused call flow in dashboard</a>


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

## Usage notes

Use this to normalize source or target table configurations before guardrails, writes, lineage, and evidence helpers use them.

This is intended for the standard pipeline table-config pattern, not for ad hoc reads or writes.


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
| `table_configs` | `list[PipelineTableConfig]` | Yes | Not documented yet |
| `default_settings` | `Mapping[str, Any] \| PipelineTableConfig` | Yes | Not documented yet |
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


!!! info "Generated reference freshness"
    Reference pages generated: 06 Jul 2026, 4:12 PM SGT
    Call-flow data generated: 06 Jul 2026, 4:08 PM SGT

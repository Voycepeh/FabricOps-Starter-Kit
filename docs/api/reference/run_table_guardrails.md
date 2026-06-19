# run_table_guardrails

Run profiling, schema, freshness, profile behavior, DQ, and catalogue guardrails for table configs.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/pipeline.py:548`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L548-L773">View on GitHub</a>
</div>

## Usage guidance

### Use when

- Use in 02_pipeline before transformations or writes when table configs should be validated by the standard guardrail sequence.

### Do not use when

- Do not use as a replacement for individual helper calls when debugging one specific guardrail interactively.

### Additional context

Coordinates profiling, schema, freshness, profile behavior, DQ, and evidence checks for a group of pipeline table configs.


## Signature

<div class="reference-api-definition" markdown="1">

```python
def run_table_guardrails(
    table_configs: list[dict[str, Any]],
    run_id: str,
    context: dict[str, Any] | None=None,
    spark_session: Any,
    agreement_id: str='',
    agreement_contract_version: str='',
    notebook_registry_id: str='',
    notebook_id: str='',
    pipeline_name: str='',
    stop_on_failure: bool=False,
) -> dict[str, Any]:
```

</div>

## Example usage

<div class="reference-example-usage" markdown="1">

```python
source_guardrail_results = run_table_guardrails(SOURCE_TABLES, config=CONFIG, env=ENV, run_id=RUN_ID, spark_session=spark, stop_on_failure=True)
```

</div>

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `table_configs` | `list[dict[str, Any]]` | Yes | Source or target table configs. Each config must contain ``key``, ``df``, and ``expected_schema``. Optional keys such as ``dataset_name``, ``stage``, ``schema_preset``, ``profile_mode``, ``profile_behavior_severity``, ``watermark_column``, ``dq_preset``, ``distribution_columns``, and ``exclude_columns`` control the guardrail behavior. |
| `run_id` | `str` | Yes | Current pipeline run identifier. |
| `context` | `dict[str, Any] \| None` | No | Advanced override for the active Fabric context. When omitted, the helper uses ``FABRIC_CONTEXT`` initialized by ``00_env_config``. |
| `spark_session` | `Any` | Yes | Spark session used by profile behavior and DQ helpers. |
| `agreement_id` | `str` | No | Governance context written with catalogue evidence. |
| `agreement_contract_version` | `str` | No | Not documented yet |
| `notebook_registry_id` | `str` | No | Not documented yet |
| `notebook_id` | `str` | No | Not documented yet |
| `pipeline_name` | `str` | No | Not documented yet |
| `stop_on_failure` | `bool` | No | When True, collect all guardrail results and catalogue evidence, then stop notebook execution via the standard guardrail stopper if any table cannot continue. |

## Returns

Guardrail result bundle with profiles, schema results, freshness results, stability results, DQ results, catalogue status, evidence definitions, summary, can_continue, and failed_tables.

### Return interpretation

The result groups each guardrail outcome and a summary DataFrame. If any blocking result has can_continue false, stop before writing data.

## Raises / Errors

Not documented yet

### Common failure causes

- One of the table configs is incomplete.
- A schema, freshness, profile behavior, or DQ check fails.
- Approved metadata evidence cannot be read.
- Spark cannot profile or validate one of the DataFrames.

## Relationships

### Used by

Not documented yet

### Calls

- `fabricops_kit.config.resolve_fabric_context`
- <a href="profile_dataframe/"><code>fabricops_kit.data_profiling.profile_dataframe</code></a>
- <a href="enforce_dq_rules/"><code>fabricops_kit.governance_review.enforce_dq_rules</code></a>
- `fabricops_kit.guardrails.enforce_freshness`
- `fabricops_kit.guardrails.enforce_freshness_rule`
- `fabricops_kit.guardrails.enforce_profile_behavior`
- `fabricops_kit.guardrails.stop_if_failed`
- `fabricops_kit.metadata._build_metadata_table_key`
- `fabricops_kit.metadata._write_guardrail_result_row`
- `fabricops_kit.pipeline._build_guardrail_blocking_message_from_bundle`
- `fabricops_kit.pipeline._build_guardrail_evidence_definitions`
- `fabricops_kit.pipeline._guardrail_can_continue`
- `fabricops_kit.pipeline._table_key`
- `fabricops_kit.pipeline._table_name`
- `fabricops_kit.pipeline.build_guardrail_detail_rows`
- `fabricops_kit.pipeline.build_guardrail_summary_rows`
- `fabricops_kit.pipeline.write_catalogue_evidence`

## Implementation details

<details class="reference-implementation-details">
<summary>Notes, side effects, and template usage</summary>

**Used in templates:**

Direct starter notebook code-cell invocations only; import-only, markdown-only, generated metadata, and internal helper calls are not counted.

- `02_pipeline`

**Side effects:**

Profiles DataFrames, reads stability/DQ metadata through configured metadata routing, writes evidence, and may update table config DataFrames with DQ annotations.

**Notes:**

This helper intentionally collects all per-table schema, freshness, profile behavior, and DQ
results before reporting blocking failures. DQ results that return an
annotated DataFrame update the corresponding table config ``df`` in place
so downstream writes use the checked DataFrame. Metadata reads and writes
are routed through the configured metadata target by the called helpers.

</details>

??? info "Call flow"

    Large call graph shown to two levels.

    Tree is truncated to keep the page readable.

    Unique internal helpers: 88. Repeated calls may appear in multiple branches.

    <div class="reference-call-tree" role="tree">
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix"></span><code>run_table_guardrails(...)</code></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L352-L358"><code>_build_guardrail_blocking_message_from_bundle(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│   ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L338-L349"><code>_blocking_guardrail_message(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│   └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L240-L303"><code>build_guardrail_summary_rows(...)</code></a></div>
      <div class="reference-call-tree-row reference-call-tree-more" role="treeitem"><span class="reference-call-tree-prefix">│       └── </span>…</div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L515-L545"><code>_build_guardrail_evidence_definitions(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│   ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L503-L504"><code>_table_key(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│   └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L507-L508"><code>_table_name(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L80-L81"><code>_build_metadata_table_key(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│   └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L75-L77"><code>_stable_metadata_key(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L92-L110"><code>_check_schema_rule_runtime(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│   ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L82-L89"><code>_apply_bypass_post_review_warning(...)</code></a></div>
      <div class="reference-call-tree-row reference-call-tree-more" role="treeitem"><span class="reference-call-tree-prefix">│   │   └── </span>…</div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│   ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L673-L684"><code>_catalogue_value(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│   ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L313-L408"><code>_check_schema_runtime(...)</code></a></div>
      <div class="reference-call-tree-row reference-call-tree-more" role="treeitem"><span class="reference-call-tree-prefix">│   │   └── </span>…</div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│   ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L46-L51"><code>_parse_rule_parameters(...)</code></a></div>
      <div class="reference-call-tree-row reference-call-tree-more" role="treeitem"><span class="reference-call-tree-prefix">│   │   └── </span>…</div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│   ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L54-L79"><code>_select_table_guardrail_rule(...)</code></a></div>
      <div class="reference-call-tree-row reference-call-tree-more" role="treeitem"><span class="reference-call-tree-prefix">│   │   └── </span>…</div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│   └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L687-L688"><code>_string_value(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L313-L408"><code>_check_schema_runtime(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│   ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L194-L209"><code>_actual_schema(...)</code></a></div>
      <div class="reference-call-tree-row reference-call-tree-more" role="treeitem"><span class="reference-call-tree-prefix">│   │   └── </span>…</div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│   └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L145-L191"><code>_normalize_datatype(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L511-L512"><code>_guardrail_can_continue(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L503-L504"><code>_table_key(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L507-L508"><code>_table_name(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L89-L136"><code>_write_guardrail_result_row(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│   ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L200-L273"><code>_build_runtime_audit_fields(...)</code></a></div>
      <div class="reference-call-tree-row reference-call-tree-more" role="treeitem"><span class="reference-call-tree-prefix">│   │   └── </span>…</div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│   ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L164-L177"><code>_configured_lakehouse_schema(...)</code></a></div>
      <div class="reference-call-tree-row reference-call-tree-more" role="treeitem"><span class="reference-call-tree-prefix">│   │   └── </span>…</div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│   ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L64-L65"><code>_now_utc_iso(...)</code></a></div>
      <div class="reference-call-tree-row reference-call-tree-more" role="treeitem"><span class="reference-call-tree-prefix">│   │   └── </span>…</div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│   └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L438-L548"><code>write_lakehouse_table(...)</code></a></div>
      <div class="reference-call-tree-row reference-call-tree-more" role="treeitem"><span class="reference-call-tree-prefix">│       └── </span>…</div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L306-L335"><code>build_guardrail_detail_rows(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│   ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L217-L227"><code>_guardrail_reason(...)</code></a></div>
      <div class="reference-call-tree-row reference-call-tree-more" role="treeitem"><span class="reference-call-tree-prefix">│   │   └── </span>…</div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│   ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L140-L151"><code>_next_action(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│   ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L126-L130"><code>_result_can_continue(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│   ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L121-L123"><code>_result_status(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│   ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L230-L237"><code>_table_keys(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│   └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L116-L118"><code>_yes_no(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L240-L303"><code>build_guardrail_summary_rows(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│   ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L217-L227"><code>_guardrail_reason(...)</code></a></div>
      <div class="reference-call-tree-row reference-call-tree-more" role="treeitem"><span class="reference-call-tree-prefix">│   │   └── </span>…</div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│   ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L140-L151"><code>_next_action(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│   ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L126-L130"><code>_result_can_continue(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│   ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L121-L123"><code>_result_status(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│   ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L230-L237"><code>_table_keys(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│   └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L116-L118"><code>_yes_no(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">├── </span><a href="../enforce_dq_rules/"><code>enforce_dq_rules(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│   ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1429-L1439"><code>_dq_failed_row_count(...)</code></a></div>
      <div class="reference-call-tree-row reference-call-tree-more" role="treeitem"><span class="reference-call-tree-prefix">│   │   └── </span>…</div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│   ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1442-L1457"><code>_dq_summary(...)</code></a></div>
      <div class="reference-call-tree-row reference-call-tree-more" role="treeitem"><span class="reference-call-tree-prefix">│   │   └── </span>…</div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│   ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1393-L1426"><code>_dq_tagged_dataframe(...)</code></a></div>
      <div class="reference-call-tree-row reference-call-tree-more" role="treeitem"><span class="reference-call-tree-prefix">│   │   └── </span>…</div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│   ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1214-L1261"><code>_load_active_dq_rules(...)</code></a></div>
      <div class="reference-call-tree-row reference-call-tree-more" role="treeitem"><span class="reference-call-tree-prefix">│   │   └── </span>…</div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│   ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1481-L1488"><code>_read_guardrail_rule_metadata(...)</code></a></div>
      <div class="reference-call-tree-row reference-call-tree-more" role="treeitem"><span class="reference-call-tree-prefix">│   │   └── </span>…</div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│   ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1355-L1390"><code>_run_dq_guardrail_checks(...)</code></a></div>
      <div class="reference-call-tree-row reference-call-tree-more" role="treeitem"><span class="reference-call-tree-prefix">│   │   └── </span>…</div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│   ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1460-L1477"><code>_summarize_dq_guardrail(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│   └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L89-L136"><code>_write_guardrail_result_row(...)</code></a></div>
      <div class="reference-call-tree-row reference-call-tree-more" role="treeitem"><span class="reference-call-tree-prefix">│       └── </span>…</div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L572-L670"><code>enforce_freshness(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│   ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L547-L564"><code>_coerce_date(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│   ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L567-L569"><code>_iso_date_value(...)</code></a></div>
      <div class="reference-call-tree-row reference-call-tree-more" role="treeitem"><span class="reference-call-tree-prefix">│   │   └── </span>…</div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│   └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L514-L544"><code>_max_column_value(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L113-L131"><code>enforce_freshness_rule(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│   ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L82-L89"><code>_apply_bypass_post_review_warning(...)</code></a></div>
      <div class="reference-call-tree-row reference-call-tree-more" role="treeitem"><span class="reference-call-tree-prefix">│   │   └── </span>…</div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│   ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L673-L684"><code>_catalogue_value(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│   ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L46-L51"><code>_parse_rule_parameters(...)</code></a></div>
      <div class="reference-call-tree-row reference-call-tree-more" role="treeitem"><span class="reference-call-tree-prefix">│   │   └── </span>…</div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│   ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L54-L79"><code>_select_table_guardrail_rule(...)</code></a></div>
      <div class="reference-call-tree-row reference-call-tree-more" role="treeitem"><span class="reference-call-tree-prefix">│   │   └── </span>…</div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│   ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L687-L688"><code>_string_value(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│   └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L572-L670"><code>enforce_freshness(...)</code></a></div>
      <div class="reference-call-tree-row reference-call-tree-more" role="treeitem"><span class="reference-call-tree-prefix">│       └── </span>…</div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L691-L913"><code>enforce_profile_behavior(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│   ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L278-L307"><code>_accepted_profile_rows(...)</code></a></div>
      <div class="reference-call-tree-row reference-call-tree-more" role="treeitem"><span class="reference-call-tree-prefix">│   │   └── </span>…</div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│   ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L82-L89"><code>_apply_bypass_post_review_warning(...)</code></a></div>
      <div class="reference-call-tree-row reference-call-tree-more" role="treeitem"><span class="reference-call-tree-prefix">│   │   └── </span>…</div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│   ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L673-L684"><code>_catalogue_value(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│   ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L164-L177"><code>_configured_lakehouse_schema(...)</code></a></div>
      <div class="reference-call-tree-row reference-call-tree-more" role="treeitem"><span class="reference-call-tree-prefix">│   │   └── </span>…</div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│   ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L492-L496"><code>_guardrail_exclude_columns(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│   ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L915-L918"><code>_is_missing_table_error(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│   ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L213-L214"><code>_json_dumps_stable(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│   ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L217-L218"><code>_profile_hash(...)</code></a></div>
      <div class="reference-call-tree-row reference-call-tree-more" role="treeitem"><span class="reference-call-tree-prefix">│   │   └── </span>…</div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│   ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L226-L247"><code>_profile_payload_from_profile(...)</code></a></div>
      <div class="reference-call-tree-row reference-call-tree-more" role="treeitem"><span class="reference-call-tree-prefix">│   │   └── </span>…</div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│   ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L251-L276"><code>_select_profile_behavior_rule(...)</code></a></div>
      <div class="reference-call-tree-row reference-call-tree-more" role="treeitem"><span class="reference-call-tree-prefix">│   │   └── </span>…</div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│   ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L687-L688"><code>_string_value(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│   ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L89-L136"><code>_write_guardrail_result_row(...)</code></a></div>
      <div class="reference-call-tree-row reference-call-tree-more" role="treeitem"><span class="reference-call-tree-prefix">│   │   └── </span>…</div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│   ├── </span><a href="../profile_dataframe/"><code>profile_dataframe(...)</code></a></div>
      <div class="reference-call-tree-row reference-call-tree-more" role="treeitem"><span class="reference-call-tree-prefix">│   │   └── </span>…</div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│   └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L382-L435"><code>read_lakehouse_table(...)</code></a></div>
      <div class="reference-call-tree-row reference-call-tree-more" role="treeitem"><span class="reference-call-tree-prefix">│       └── </span>…</div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">├── </span><a href="../profile_dataframe/"><code>profile_dataframe(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│   ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L216-L221"><code>_audit_timestamp_expr(...)</code></a></div>
      <div class="reference-call-tree-row reference-call-tree-more" role="treeitem"><span class="reference-call-tree-prefix">│   │   └── </span>…</div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│   ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_profiling.py#L193-L223"><code>_build_distribution_summaries(...)</code></a></div>
      <div class="reference-call-tree-row reference-call-tree-more" role="treeitem"><span class="reference-call-tree-prefix">│   │   └── </span>…</div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│   ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L199-L204"><code>_get_audit_timezone(...)</code></a></div>
      <div class="reference-call-tree-row reference-call-tree-more" role="treeitem"><span class="reference-call-tree-prefix">│   │   └── </span>…</div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│   ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_profiling.py#L59-L82"><code>_get_profiled_columns(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│   └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_profiling.py#L85-L105"><code>_is_min_max_supported_type(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L141-L161"><code>resolve_fabric_context(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│   └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L26-L83"><code>get_default_fabric_context(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L921-L941"><code>stop_if_failed(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│   └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L134-L142"><code>SchemaDriftError(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">└── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L776-L882"><code>write_catalogue_evidence(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L80-L81"><code>_build_metadata_table_key(...)</code></a></div>
      <div class="reference-call-tree-row reference-call-tree-more" role="treeitem"><span class="reference-call-tree-prefix">    │   └── </span>…</div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L64-L92"><code>_canonical_catalogue_profile_df(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L164-L177"><code>_configured_lakehouse_schema(...)</code></a></div>
      <div class="reference-call-tree-row reference-call-tree-more" role="treeitem"><span class="reference-call-tree-prefix">    │   └── </span>…</div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L24-L25"><code>_definition_name(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L95-L112"><code>_normalize_catalogue_evidence_types(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L20-L21"><code>_now_iso(...)</code></a></div>
      <div class="reference-call-tree-row reference-call-tree-more" role="treeitem"><span class="reference-call-tree-prefix">    │   └── </span>…</div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L50-L61"><code>_runtime_audit_fields(...)</code></a></div>
      <div class="reference-call-tree-row reference-call-tree-more" role="treeitem"><span class="reference-call-tree-prefix">    │   └── </span>…</div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L438-L548"><code>write_lakehouse_table(...)</code></a></div>
      <div class="reference-call-tree-row reference-call-tree-more" role="treeitem"><span class="reference-call-tree-prefix">        └── </span>…</div>
    </div>


<details class="reference-metadata-details">
<summary>Machine-readable metadata / metadata details</summary>

These generated fields are for automation tooling, maintainers, and documentation tooling. Skip this block when reading the docs normally.

### Function manifest

- Fully qualified function name: `fabricops_kit.pipeline.run_table_guardrails`
- Short name: `run_table_guardrails`
- Module: `pipeline`
- Classification: Callable
- Related module: `pipeline`
- Source file path: `src/fabricops_kit/pipeline.py`
- Source line: `548`
- Inbound references count: 0
- Outbound references count: 17
- Used in templates: 02_pipeline
- Glossary terms: guardrails, can_continue, source data, target table, evidence

### Implementation contract

- **required_context:** Requires CONFIG and env from 00_env_config so metadata operations use the configured metadata target.
- **inputs:** table_configs plus config, env, run_id, spark_session, and agreement/notebook context.
- **output:** Guardrail result bundle with profiles, schema results, freshness results, stability results, DQ results, catalogue status, evidence definitions, summary, can_continue, and failed_tables.
- **side_effects:** Profiles DataFrames, reads stability/DQ metadata through configured metadata routing, writes evidence, and may update table config DataFrames with DQ annotations.
- **failure_modes:** Not documented yet
- **verification:** Verify stop_on_failure=True is used before transformation or writes when blocking guardrails should stop execution.

### Inbound references

Not documented yet

### Outbound references

- `fabricops_kit.config.resolve_fabric_context`
- <a href="profile_dataframe/"><code>fabricops_kit.data_profiling.profile_dataframe</code></a>
- <a href="enforce_dq_rules/"><code>fabricops_kit.governance_review.enforce_dq_rules</code></a>
- `fabricops_kit.guardrails.enforce_freshness`
- `fabricops_kit.guardrails.enforce_freshness_rule`
- `fabricops_kit.guardrails.enforce_profile_behavior`
- `fabricops_kit.guardrails.stop_if_failed`
- `fabricops_kit.metadata._build_metadata_table_key`
- `fabricops_kit.metadata._write_guardrail_result_row`
- `fabricops_kit.pipeline._build_guardrail_blocking_message_from_bundle`
- `fabricops_kit.pipeline._build_guardrail_evidence_definitions`
- `fabricops_kit.pipeline._guardrail_can_continue`
- `fabricops_kit.pipeline._table_key`
- `fabricops_kit.pipeline._table_name`
- `fabricops_kit.pipeline.build_guardrail_detail_rows`
- `fabricops_kit.pipeline.build_guardrail_summary_rows`
- `fabricops_kit.pipeline.write_catalogue_evidence`

### Raw source metadata

- Source file path: `src/fabricops_kit/pipeline.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L548-L773">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L548-L773</a>
- Start line: `548`
- End line: `773`
- Signature:

```python
def run_table_guardrails(
    table_configs: list[dict[str, Any]],
    run_id: str,
    context: dict[str, Any] | None=None,
    spark_session: Any,
    agreement_id: str='',
    agreement_contract_version: str='',
    notebook_registry_id: str='',
    notebook_id: str='',
    pipeline_name: str='',
    stop_on_failure: bool=False,
) -> dict[str, Any]:
```

### Internal relationship graph

### Public related functions

- <a href="prepare_pipeline_table_configs/"><code>fabricops_kit.pipeline.prepare_pipeline_table_configs</code></a>
- `fabricops_kit.pipeline.write_catalogue_evidence`

### Internal implementation summary

- Internal helper count: 88
- Grouped helper summary is rendered in the page-level Implementation details section; helper chips link to source.

</details>

## Glossary

- <details class="glossary-chip"><summary>Guardrails</summary>Approved checks that evaluate schema, freshness, profile behavior, or DQ expectations during a pipeline run.</details>
- <details class="glossary-chip"><summary>can_continue</summary>Boolean result that tells downstream notebook code whether processing can keep running.</details>
- <details class="glossary-chip"><summary>Source data</summary>Input data read from configured upstream files, tables, Lakehouses, or Warehouses before transformation.</details>
- <details class="glossary-chip"><summary>Target table</summary>A written table produced by a pipeline output.</details>
- <details class="glossary-chip"><summary>Evidence</summary>Stored proof that a profile, decision, result, or relationship existed at a point in time.</details>

See the [full glossary](../../../reference/glossary/) for more FabricOps terms.

## See also

- [Pipeline Guardrails](../../how-fabricops-works/pipeline-guardrails.md)

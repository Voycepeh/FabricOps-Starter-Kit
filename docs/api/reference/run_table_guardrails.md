# `run_table_guardrails`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview reference-lifecycle-chip-prominent">Preview</span>
<span class="reference-chip reference-chip-muted">Public function</span>
</p>

> This function is available for evaluation but is not part of the supported Live release contract. It may change without backward-compatibility guarantees.

Run approved table checks and return whether the pipeline may continue.

<div class="reference-docstring-intro" markdown="1">

Runs schema, freshness, profile-change, and DQ checks for each prepared
table configuration, saves runtime outcomes where configured, and returns
whether the notebook can continue.

</div>

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/pipeline/run_table_guardrails.py:10`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline/run_table_guardrails.py#L10-L38">View on GitHub</a>
</div>

<p class="reference-catalogue-item-meta reference-catalogue-item-badges">
<span class="reference-chip">Public Starter Kit function</span>
<span class="reference-chip">example_dq_rule_smoke_test</span>
</p>

**Used in notebooks:** `example_dq_rule_smoke_test`

## Usage notes

Use this as part of the standard Starter Kit pipeline flow. Pipeline helpers prepare, validate, profile, write, and document pipeline data in a consistent way across notebooks.

For profiling-related pipeline functions, the output captures the important details and profile of the data so downstream users can review the dataset consistently instead of relying on one-off summaries.


## Signature

<div class="reference-api-definition" markdown="1">

```python
def run_table_guardrails(
    table_configs: list[dict[str, Any]],
    run_id: str | None=None,
    context: dict[str, Any] | None=None,
    spark_session: Any | None=None,
    agreement_id: str='',
    agreement_version: str='',
    table_role: str='',
    mode: str='profile',
    stop_on_failure: bool | None=None,
) -> dict[str, Any]:
```

</div>

## Example usage

<div class="reference-example-usage" markdown="1">

```python
source_guardrail_results = run_table_guardrails(SOURCE_TABLES, run_id=RUN_ID, context={"config": CONFIG, "env": ENV}, spark_session=spark, stop_on_failure=True)
```

</div>

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `table_configs` | `list[dict[str, Any]]` | Yes | Source or target table configuration dictionaries. Each item supplies the DataFrame to check plus table identity, expected schema, freshness, profile-behavior, and DQ settings. |
| `run_id` | `str \| None` | No | Pipeline run identifier written with saved results and used to group in-memory profiles. Omit only when an active pipeline context already provides it. |
| `context` | `dict[str, Any] \| None` | No | FabricOps runtime context, usually {"config": CONFIG, "env": ENV}. Omit when 00_env_config or an active pipeline context already provides the context. |
| `spark_session` | `Any \| None` | No | Spark session used for profiling, metadata reads, DQ checks, and result writes. Omit only when an active pipeline context already provides it. |
| `agreement_id` | `str` | No | Optional data agreement identifier to attach to saved profiling and catalogue results. Omit when the active pipeline context supplies it or when no agreement context is needed. |
| `agreement_version` | `str` | No | Optional data agreement version to attach to saved profiling and catalogue results. Omit when the active pipeline context supplies it or when no agreement context is needed. |
| `table_role` | `str` | No | Optional role for the supplied configurations, usually "source" or "target". Use it when the active pipeline context should remember these definitions for summaries. |
| `mode` | `str` | No | Run mode. "profile" is the default review-oriented mode; "enforce" defaults stop_on_failure to True so blocking failures stop the notebook. |
| `stop_on_failure` | `bool \| None` | No | Whether to stop notebook execution after all table checks have been collected when any table has a blocking failure. Omit to use the default for mode. |

## Returns

Guardrail result bundle with profiles, schema results, freshness results, stability results, DQ results, catalogue status, evidence definitions, summary, can_continue, and failed_tables.

### Return interpretation

Review per-table profiles, schema results, freshness results, profile-behavior results, DQ results, catalogue status, the overall summary, can_continue, and failed_tables. True can_continue means no blocking guardrail result requires the pipeline to stop. False means the notebook should stop before writing the affected output.

## Raises / Errors

Raises ValueError when required runtime context such as spark_session or run_id is missing, when mode is unsupported, or when table configs are invalid. With stop_on_failure=True, raises or exits after all checks are collected if blocking failures exist.

### Common failure causes

- One of the table configs is incomplete.
- A schema, freshness, profile behavior, or DQ check fails.
- Approved metadata evidence cannot be read.
- Spark cannot profile or validate one of the DataFrames.

## See also

- [Pipeline Execution](../../guided-demo/run-pipeline.md)


<details>
<summary>Maintainer architecture details</summary>

## Contract impact

| Property | Value |
| --- | --- |
| Lifecycle | <span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview">Preview</span> |
| Live since | — |
| Discontinued in | — |
| Contract classification | Preview public function |
| Contract risk | Preview |
| Live-critical dependencies | 0 |

### Release history

| Status | Version |
| --- | --- |
| Preview | 0.1.0 |


</details>

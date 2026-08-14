# `check_freshness`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview reference-lifecycle-chip-prominent">Preview</span>
<span class="reference-chip reference-chip-muted">Public function</span>
</p>

> This function is available for evaluation but is not part of the supported Live release contract. It may change without backward-compatibility guarantees.

Check whether source timing satisfies direct or approved freshness intent.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/pipeline/check_freshness.py:10`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline/check_freshness.py#L10-L105">View on GitHub</a>
</div>

<p class="reference-catalogue-item-meta reference-catalogue-item-badges">
<span class="reference-chip">Public Starter Kit function</span>
<span class="reference-chip">02_pipeline</span>
</p>

**Used in notebooks:** `02_pipeline`

## Usage notes

Use this as part of the standard Starter Kit pipeline flow. Pipeline helpers prepare, validate, profile, write, and document pipeline data in a consistent way across notebooks.

For profiling-related pipeline functions, the output captures the important details and profile of the data so downstream users can review the dataset consistently instead of relying on one-off summaries.


## Signature

<div class="reference-api-definition" markdown="1">

```python
def check_freshness(
    dataframe,
    freshness_column: str | None=None,
    max_lag_days: int | str | None=None,
    severity: str='blocking',
    reference_date: date | datetime | str | None=None,
    rules_df=None,
    dataset_name: str='',
    table_name: str='',
    environment_name: str='',
    metadata_table_key: str='',
) -> dict:
```

</div>

## Example usage

<div class="reference-example-usage" markdown="1">

>>> result = check_freshness(rows, "business_date", 2)

</div>

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `dataframe` | `Any` | Yes | Spark DataFrame or iterable of row-like mappings. |
| `freshness_column` | `str \| None` | No | Column whose maximum date is the latest source observation. |
| `max_lag_days` | `int \| str \| None` | No | Maximum permitted lag in days. |
| `severity` | `str` | No | Failure behavior for a direct check. |
| `reference_date` | `date \| datetime \| str \| None` | No | Comparison date, defaulting to today. |
| `rules_df` | `DataFrame or iterable of mappings` | No | Approved rules used instead of direct freshness arguments. Canonical observation input loads the active rule automatically when omitted. If a rule retains ``freshness_column`` for direct checks, it must match the observation's governed ``change_column``. |
| `dataset_name` | `str` | No | Table identity used to select an approved rule. |
| `table_name` | `str` | No | Not documented yet |
| `environment_name` | `str` | No | Not documented yet |
| `metadata_table_key` | `str` | No | Not documented yet |

## Returns

Structured freshness evidence and continuation decision.

## Raises / Errors

Not documented yet

## See also

No related guides documented.


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


</details>

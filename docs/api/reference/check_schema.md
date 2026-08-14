# `check_schema`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview reference-lifecycle-chip-prominent">Preview</span>
<span class="reference-chip reference-chip-muted">Public function</span>
</p>

> This function is available for evaluation but is not part of the supported Live release contract. It may change without backward-compatibility guarantees.

Check observed table schema against direct or approved schema intent.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/pipeline/check_schema.py:6`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline/check_schema.py#L6-L63">View on GitHub</a>
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
def check_schema(
    dataframe,
    expected_schema: dict[str, str] | None=None,
    preset: str='strict',
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

>>> result = check_schema(df, {"order_id": "bigint"})
>>> result["can_continue"]
True

</div>

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `dataframe` | `Any` | Yes | Spark, pandas, or dataframe-like object with schema metadata. |
| `expected_schema` | `dict[str, str] \| None` | No | Expected column-to-datatype mapping for a direct check. |
| `preset` | `str` | No | Direct schema comparison behavior. |
| `rules_df` | `DataFrame or iterable of mappings` | No | Approved guardrail rules. When supplied, the applicable schema rule is selected using the table context instead of ``expected_schema``. |
| `dataset_name` | `str` | No | Table identity used to select an approved rule. |
| `table_name` | `str` | No | Not documented yet |
| `environment_name` | `str` | No | Not documented yet |
| `metadata_table_key` | `str` | No | Not documented yet |

## Returns

Structured schema guardrail status, continuation decision, checks, and differences.

## Raises / Errors

ValueError
    If the preset is invalid or neither rule data nor an expected schema is
    supplied.

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

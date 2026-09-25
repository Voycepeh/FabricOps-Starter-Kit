# `validate_data_contract`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview reference-lifecycle-chip-prominent">Preview</span>
<span class="reference-chip reference-chip-muted">Public function</span>
</p>

> This function is available for evaluation but is not part of the supported Live release contract. It may change without backward-compatibility guarantees.

Validate one exact frozen Data Contract against target data without changing business data.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/pipeline/validate_data_contract.py:21`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline/validate_data_contract.py#L21-L224">View on GitHub</a>
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
def validate_data_contract(
    table_id: str,
    contract_id: str,
    contract_version: int,
    dataframe=None,
    spark_session=None,
    run_id: str='',
    verbose: bool=True,
) -> dict[str, Any]:
```

</div>

## Example usage

<div class="reference-example-usage" markdown="1">

>>> result = validate_data_contract(
...     table_id="lakehouse||silver||dbo||orders",
...     contract_id="4f41a6a0-79ce-4d56-9872-b6775de6bb55",
...     contract_version=2,
... )
>>> result["can_activate"]
True

</div>

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `table_id` | `str` | Yes | Canonical Catalogue identity of the target table. |
| `contract_id` | `str` | Yes | Exact Data Contract lifecycle identity. |
| `contract_version` | `int` | Yes | Exact immutable version to validate. Draft versions are rejected. |
| `dataframe` | `pyspark.sql.DataFrame` | No | Target data to evaluate. When omitted, the registered table is read. |
| `spark_session` | `object` | No | Spark session to use. When omitted, FabricOps uses the supplied DataFrame session or resolves the active Microsoft Fabric session. |
| `run_id` | `str` | No | Validation execution identity. The Fabric activity identity is used when omitted. |
| `verbose` | `bool` | No | Print one concise validation summary when ``True``. |

## Returns

Exact execution identity, aggregate outcome counts, per-rule outcomes, caller-visible DQ failure details, and can_activate.

## Raises / Errors

ValueError
    If the Catalogue target or exact immutable contract is missing,
    ambiguous, malformed, still draft, or belongs to another table.
RuntimeError
    If a Spark session is unavailable.

## Notes

<div class="reference-docstring-notes" markdown="1">

This Engineering/data-plane operation only reads business data. It writes
aggregate outcomes to ``METADATA_GUARDRAIL_RESULTS`` with
``execution_type='validate'`` and never calls ``pipeline_write``. Schema
and Data Quality use the same evaluator cores as normal enforcement checks.
Freshness, Source Drift, and Sensitive Data are reported as
``not_applicable`` because validation lacks the legitimate enforcement
pipeline observation or transformation context they require. This
applicability state is neither a pass nor an activation blocker.

</div>

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

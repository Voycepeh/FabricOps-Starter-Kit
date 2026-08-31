# `check_dq`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview reference-lifecycle-chip-prominent">Preview</span>
<span class="reference-chip reference-chip-muted">Public function</span>
</p>

> This function is available for evaluation but is not part of the supported Live release contract. It may change without backward-compatibility guarantees.

Evaluate current active governed DQ rules and persist linked rule and failed-row evidence.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/pipeline/check_dq.py:7`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline/check_dq.py#L7-L80">View on GitHub</a>
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
def check_dq(
    dataframe,
    table_id: str,
    dataset_name: str='',
    run_id: str='',
    row_identity_columns: list[str] | None=None,
) -> dict:
```

</div>

## Example usage

<div class="reference-example-usage" markdown="1">

>>> result = check_dq(source_df, table_id="lakehouse||source||dbo||orders", row_identity_columns=["order_id"])
>>> result["can_continue"]
True

</div>

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `dataframe` | `pyspark.sql.DataFrame` | Yes | Source or target rows to evaluate without filtering or copying complete rows into metadata. |
| `table_id` | `str` | Yes | Canonical identity of an active registered Catalogue table. |
| `dataset_name` | `str` | No | Governed dataset identity used to further scope rules when supplied. |
| `run_id` | `str` | No | Pipeline run identity persisted with failed-row evidence. When omitted, the current Fabric activity identity is used. |
| `row_identity_columns` | `list[str] \| None` | No | Business-key columns used for row identity. When omitted, an existing row UUID/ID is preferred and a deterministic content hash is the fallback. |

## Returns

Overall DQ status, continuation decision, per-rule checks, aggregate counts, and a tagged DataFrame.

## Raises / Errors

ValueError
    If configured identity columns are absent or governed rule metadata is
    invalid.
RuntimeError
    If Spark is unavailable in the Microsoft Fabric runtime.

## Notes

<div class="reference-docstring-notes" markdown="1">

Production resolves the physical table through the Catalogue and evaluates
frozen DQ rules from its active Data Contract. Development evaluates current
active approved authoring rules in ``METADATA_GUARDRAIL``.
Every evaluated rule/run is appended to ``METADATA_GUARDRAIL_RESULTS``;
only failed row/rule pairs are appended to
``METADATA_GUARDRAIL_ROW_RESULTS``. Error failures block continuation while
warning failures do not.

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

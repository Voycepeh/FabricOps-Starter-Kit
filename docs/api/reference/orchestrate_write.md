# `orchestrate_write`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview reference-lifecycle-chip-prominent">Preview</span>
<span class="reference-chip reference-chip-muted">Public function</span>
</p>

> This function is available for evaluation but is not part of the supported Live release contract. It may change without backward-compatibility guarantees.

Run the observable standard governed target lifecycle.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/pipeline/orchestrate_write.py:15`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline/orchestrate_write.py#L15-L111">View on GitHub</a>
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
def orchestrate_write(
    dataframe: Any,
    name: str,
    sources: Iterable[dict[str, Any]],
    store: str,
    schema: str | None,
    table_name: str,
    write_mode: str,
    contracts: dict[str, Any] | None=None,
    repartition_by: int | None=None,
    spark_session=None,
    verbose: bool=True,
) -> dict[str, Any]:
```

</div>

## Example usage

<div class="reference-example-usage" markdown="1">

>>> result = orchestrate_write(transformed_df, name="curated_orders", sources=[orders], store="Silver", schema="demo", table_name="curated_orders", write_mode="overwrite", contracts=CONTRACTS)

</div>

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `dataframe` | `Any` | Yes | Transformed Spark DataFrame to validate and publish. |
| `name` | `str` | Yes | Notebook-facing target name used in orchestration output. |
| `sources` | `Iterable[dict[str, Any]]` | Yes | Governed source results containing ``table_id``. |
| `store` | `str` | Yes | Configured destination store key. |
| `schema` | `str \| None` | Yes | Physical target schema. |
| `table_name` | `str` | Yes | Physical target table name. |
| `write_mode` | `str` | Yes | Notebook-facing Write mode forwarded to :func:`pipeline_write` as its governed load strategy. |
| `contracts` | `dict[str, Any] \| None` | No | ``widget_select_data_contract`` result used to choose Validate or Enforce publication behaviour. Both modes run the same Guardrails. |
| `repartition_by` | `int \| None` | No | Spark write partition count. |
| `spark_session` | `object` | No | Spark session used by every stage. |
| `verbose` | `bool` | No | Print stage start, outcome, duration, and failure attribution. |

## Returns

Publication identity and every stage result, or a successful validation-only result.

## Raises / Errors

RuntimeError
    If any stage fails. Its name is reported and the original exception is
    retained as ``__cause__``.

## Notes

<div class="reference-docstring-notes" markdown="1">

Both contract modes run Schema, Sensitive Data, Source Drift, Data Quality,
and Guardrail Coverage identically. Validate then returns without writing;
Enforce continues through Write and persisted-target Profile. Existing
metadata and Source Observation commit behaviour remains owned by
``pipeline_write``. No DataFrame is displayed.

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

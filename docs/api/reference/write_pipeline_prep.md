# `write_pipeline_prep`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview reference-lifecycle-chip-prominent">Preview</span>
<span class="reference-chip reference-chip-muted">Public function</span>
</p>

> This function is available for evaluation but is not part of the supported Live release contract. It may change without backward-compatibility guarantees.

Prepare governed target write inputs and technical fields without physically writing.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/pipeline/write_pipeline_prep.py:27`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline/write_pipeline_prep.py#L27-L135">View on GitHub</a>
</div>

<p class="reference-catalogue-item-meta reference-catalogue-item-badges">
<span class="reference-chip">Public Starter Kit function</span>
<span class="reference-chip">Usage detection may exclude indirect or generated references.</span>
</p>

**Used in notebooks:** Usage detection may exclude indirect or generated references.

## Usage notes

Use this as part of the standard Starter Kit pipeline flow. Pipeline helpers prepare, validate, profile, write, and document pipeline data in a consistent way across notebooks.

For profiling-related pipeline functions, the output captures the important details and profile of the data so downstream users can review the dataset consistently instead of relying on one-off summaries.


## Signature

<div class="reference-api-definition" markdown="1">

```python
def write_pipeline_prep(
    df,
    read_prep: dict[str, Any],
    target: str='unified',
) -> dict[str, Any]:
```

</div>

## Example usage

<div class="reference-example-usage" markdown="1">

>>> write_prep = write_pipeline_prep(transformed_df, read_prep, target="unified")
>>> write_prep["mode"]
'append'

</div>

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `df` | `pyspark.sql.DataFrame` | Yes | Business target DataFrame after target schema and DQ checks pass. |
| `read_prep` | `dict[str, Any]` | Yes | Exact result returned by :func:`read_pipeline_prep`. Its canonical ``processing`` definition is reused without contract re-resolution. |
| `target` | `str` | No | Configured Lakehouse or Warehouse target used to prepare physical writer settings. |

## Returns

Audited DataFrame, writer mode/options, canonical processing, and prepared execution scope.

## Raises / Errors

ValueError
    If preparation is incomplete or an unsafe target/strategy combination
    is requested.

## Notes

<div class="reference-docstring-notes" markdown="1">

FabricOps resolves one run-level audit record and adds only compact target
provenance fields. This function does not call a Lakehouse or Warehouse
writer or commit source progress. The completion context has no effect
unless explicitly passed to a FabricOps writer. Lakehouse and Warehouse
targets use the same governed strategy definition; each writer applies its
engine-specific physical execution only after this preparation succeeds.

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

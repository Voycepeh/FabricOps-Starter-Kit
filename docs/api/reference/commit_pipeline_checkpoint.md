# `commit_pipeline_checkpoint`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview reference-lifecycle-chip-prominent">Preview</span>
<span class="reference-chip reference-chip-muted">Public function</span>
</p>

> This function is available for evaluation but is not part of the supported Live release contract. It may change without backward-compatibility guarantees.

Commit a prepared watermark after the governed target write succeeds.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/pipeline/commit_pipeline_checkpoint.py:10`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline/commit_pipeline_checkpoint.py#L10-L88">View on GitHub</a>
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
def commit_pipeline_checkpoint(read_prep: dict[str, Any]) -> dict[str, Any] | None
```

</div>

## Example usage

<div class="reference-example-usage" markdown="1">

>>> write_lakehouse_table(
...     write_prep["df"], "bookings",
...     mode=write_prep["mode"], options=write_prep["options"],
... )
>>> committed = commit_pipeline_checkpoint(read_prep)
>>> committed is None or committed["watermark_column"] == "modified_datetime"
True

</div>

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `read_prep` | `dict[str, Any]` | Yes | Exact result returned by :func:`read_pipeline_prep`. Call this function only after transformation, Guardrails, and the physical target write have all succeeded. |

## Returns

The committed checkpoint record, or None when no watermark candidate exists.

## Raises / Errors

ValueError
    If the preparation result contains an invalid watermark candidate or
    inconsistent source identity.
RuntimeError
    If Fabric configuration, Spark, or metadata persistence is unavailable.

## Notes

<div class="reference-docstring-notes" markdown="1">

This is the explicit success boundary for watermark processing.
``read_pipeline_prep`` never advances successful state. If a target write
raises, do not call this function; the previous successful checkpoint then
remains unchanged and the same bounded range is prepared on retry.

Metadata and business targets may be separate Fabric items, so the target
write and checkpoint append cannot form one cross-item transaction. Target
writes used with watermark retries must therefore be idempotent.

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

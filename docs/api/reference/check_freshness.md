# `check_freshness`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview reference-lifecycle-chip-prominent">Preview</span>
<span class="reference-chip reference-chip-muted">Public function</span>
</p>

> This function is available for evaluation but is not part of the supported Live release contract. It may change without backward-compatibility guarantees.

Check whether source timing satisfies direct or approved freshness intent.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/pipeline/check_freshness.py:20`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline/check_freshness.py#L20-L163">View on GitHub</a>
</div>

<p class="reference-catalogue-item-meta reference-catalogue-item-badges">
<span class="reference-chip">Public Starter Kit function</span>
<span class="reference-chip">02_pipeline</span>
<span class="reference-chip">03_incremental_pipeline</span>
</p>

**Used in notebooks:** `02_pipeline`, `03_incremental_pipeline`

## Usage notes

Use this as part of the standard Starter Kit pipeline flow. Pipeline helpers prepare, validate, profile, write, and document pipeline data in a consistent way across notebooks.

For profiling-related pipeline functions, the output captures the important details and profile of the data so downstream users can review the dataset consistently instead of relying on one-off summaries.


## Signature

<div class="reference-api-definition" markdown="1">

```python
def check_freshness(
    table_id: str,
    enabled: bool=True,
    raise_on_failure: bool=False,
    verbose: bool=True,
) -> dict:
```

</div>

## Example usage

<div class="reference-example-usage" markdown="1">

>>> result = check_freshness(source_result["table_id"])

</div>

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `table_id` | `str` | Yes | Canonical governed source identity returned by :func:`pipeline_read`. |
| `enabled` | `bool` | No | Explicitly disable this check when ``False``. Normally omit this value; FabricOps enforces the resolved pipeline Data Contract automatically. |
| `raise_on_failure` | `bool` | No | Raise ``RuntimeError`` when a blocking freshness result cannot continue. |
| `verbose` | `bool` | No | Print the concise normalized check outcome when ``True``. |

## Returns

Structured freshness evidence and continuation decision.

## Raises / Errors

ValueError
    If the observation or configured freshness rule is invalid.
RuntimeError
    If ``raise_on_failure=True`` and a blocking freshness result cannot
    continue.

## Notes

<div class="reference-docstring-notes" markdown="1">

Production resolves expectations from the active Data Contract. Development
uses an explicitly selected immutable version, or safely skips when none is
selected.

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

### Release history

| Status | Version |
| --- | --- |
| Preview | 0.2.0 |


</details>

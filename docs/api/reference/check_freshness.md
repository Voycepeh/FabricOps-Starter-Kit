# `check_freshness`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview reference-lifecycle-chip-prominent">Preview</span>
<span class="reference-chip reference-chip-muted">Public function</span>
</p>

> This function is available for evaluation but is not part of the supported Live release contract. It may change without backward-compatibility guarantees.

Check whether source timing satisfies direct or approved freshness intent.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/pipeline/check_freshness.py:39`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline/check_freshness.py#L39-L152">View on GitHub</a>
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
def check_freshness(observation, *, table_id: str | None=None) -> dict
```

</div>

## Example usage

<div class="reference-example-usage" markdown="1">

>>> observation = observe_table("orders", target="source", schema="dbo")
>>> result = check_freshness(observation)

</div>

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `observation` | `pyspark.sql.DataFrame` | Yes | Canonical evidence returned by :func:`observe_table`. |
| `table_id` | `str \| None` | No | Canonical registered table identity. When supplied, it must match the identity carried by the observation. |

## Returns

Structured freshness evidence and continuation decision.

## Raises / Errors

Not documented yet

## Notes

<div class="reference-docstring-notes" markdown="1">

Production resolves freshness and observation-column expectations from the
active frozen Data Contract. Development uses mutable authoring metadata.

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

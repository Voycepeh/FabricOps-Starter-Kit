# `check_source_drift`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview reference-lifecycle-chip-prominent">Preview</span>
<span class="reference-chip reference-chip-muted">Public function</span>
</p>

> This function is available for evaluation but is not part of the supported Live release contract. It may change without backward-compatibility guarantees.

Validate source changes against one target consumption baseline using the source's governed load behaviour.

<div class="reference-docstring-intro" markdown="1">

Compare the current source observation with the last source observation
successfully consumed by this target and detect source changes that violate
the source table's governed load behaviour.

</div>

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/pipeline/check_source_drift.py:13`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline/check_source_drift.py#L13-L151">View on GitHub</a>
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
def check_source_drift(
    source_table_id: str,
    target_table_id: str,
    enabled: bool=True,
    raise_on_failure: bool=False,
    verbose: bool=True,
) -> dict:
```

</div>

## Example usage

<div class="reference-example-usage" markdown="1">

>>> result = check_source_drift(
...     source_result["table_id"],
...     target_table_id=target_table_id,
... )
>>> result["target_table_id"] == target_table_id
True

</div>

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `source_table_id` | `str` | Yes | Canonical governed source identity returned by :func:`pipeline_read`. |
| `target_table_id` | `str` | Yes | Canonical governed target identity used to select the last successfully consumed Source Observation baseline. |
| `enabled` | `bool` | No | Explicitly skip the check when ``False``. |
| `raise_on_failure` | `bool` | No | Raise ``RuntimeError`` when a blocking result cannot continue. |
| `verbose` | `bool` | No | Print the concise normalized check outcome when ``True``. |

## Returns

First-observation, changed or unchanged, and new, changed, removed, or reappeared partition evidence.

## Raises / Errors

ValueError
    If either identity, transient observation, rule, or source processing
    definition is invalid.
RuntimeError
    If metadata history cannot be read, or ``raise_on_failure=True`` and
    the target cannot safely reconcile the observed source change.

## Notes

<div class="reference-docstring-notes" markdown="1">

Notebook orchestration calls this function explicitly for every governed
source before :func:`pipeline_write`. A successful write then commits the
accepted source-to-target baseline in ``METADATA_SOURCE_OBSERVATION``.

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

# `check_schema`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview reference-lifecycle-chip-prominent">Preview</span>
<span class="reference-chip reference-chip-muted">Public function</span>
</p>

> This function is available for evaluation but is not part of the supported Live release contract. It may change without backward-compatibility guarantees.

Check observed table schema against direct or approved schema intent.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/pipeline/check_schema.py:20`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline/check_schema.py#L20-L134">View on GitHub</a>
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
    table_id: str,
    dataframe=None,
    enabled: bool=True,
    raise_on_failure: bool=False,
) -> dict:
```

</div>

## Example usage

<div class="reference-example-usage" markdown="1">

>>> result = check_schema(table_id="lakehouse||source||dbo||orders")
>>> result["can_continue"]
True

</div>

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `table_id` | `str` | Yes | Canonical identity of an active registered Catalogue table. |
| `dataframe` | `DataFrame` | No | Incoming DataFrame whose schema should be checked. When omitted, the schema of the configured physical table is checked. |
| `enabled` | `bool` | No | Whether Data Contract validation is enabled for this notebook run. ``False`` returns a continuation-safe skipped result without metadata IO. |
| `raise_on_failure` | `bool` | No | Raise ``RuntimeError`` when a blocking schema result cannot continue. |

## Returns

Structured schema guardrail status, continuation decision, checks, and differences.

## Raises / Errors

ValueError
    If the target is unsupported or no active approved Schema guardrail
    exists for the resolved table.
RuntimeError
    If ``raise_on_failure=True`` and a blocking schema result cannot
    continue.

## Notes

<div class="reference-docstring-notes" markdown="1">

Production resolves the physical table through the Catalogue and uses its
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

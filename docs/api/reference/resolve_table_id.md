# `resolve_table_id`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview reference-lifecycle-chip-prominent">Preview</span>
<span class="reference-chip reference-chip-muted">Public function</span>
</p>

> This function is available for evaluation but is not part of the supported Live release contract. It may change without backward-compatibility guarantees.

Resolve deterministic target identity before its first Development write.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/pipeline/resolve_table_id.py:7`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline/resolve_table_id.py#L7-L45">View on GitHub</a>
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
def resolve_table_id(*, target: str, schema: str | None=None, table_name: str) -> str
```

</div>

## Example usage

<div class="reference-example-usage" markdown="1">

>>> table_id = resolve_table_id(
...     target="unified", schema="dbo", table_name="curated_orders"
... )

</div>

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `target` | `str` | Yes | Configured FabricStore target key. |
| `schema` | `str \| None` | No | Physical schema, or ``None`` when the configured store does not use one. |
| `table_name` | `str` | Yes | Physical table name. |

## Returns

Deterministic canonical table_id for the configured physical identity.

## Raises / Errors

ValueError
    If the target, schema, table name, or configured store is invalid.

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

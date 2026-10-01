# `build_consumer_context`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview reference-lifecycle-chip-prominent">Preview</span>
<span class="reference-chip reference-chip-muted">Public function</span>
</p>

> This function is available for evaluation but is not part of the supported Live release contract. It may change without backward-compatibility guarantees.

Build deterministic consumer context for one active governed Production table.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/consumption/build_consumer_context.py:8`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/consumption/build_consumer_context.py#L8-L58">View on GitHub</a>
</div>

<p class="reference-catalogue-item-meta reference-catalogue-item-badges">
<span class="reference-chip">Public Starter Kit function</span>
<span class="reference-chip">Usage detection may exclude indirect or generated references.</span>
</p>

**Used in notebooks:** Usage detection may exclude indirect or generated references.

## Usage notes

Do not use for Development data or multi-table relationship modelling.


## Signature

<div class="reference-api-definition" markdown="1">

```python
def build_consumer_context(
    table_id: str,
    config: Any=None,
    context: Mapping[str, Any] | None=None,
    spark_session: Any=None,
) -> dict[str, Any]:
```

</div>

## Example usage

<div class="reference-example-usage" markdown="1">

>>> context = build_consumer_context("lakehouse||production||dbo||orders")
>>> context["environment"]
'prod'

</div>

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `table_id` | `str` | Yes | Canonical FabricOps table identity. |
| `config` | `Any` | No | FabricOps configuration. The configured notebook value is used when omitted. |
| `context` | `Mapping[str, Any] \| None` | No | FabricOps runtime context used to resolve configuration and Spark. |
| `spark_session` | `Any` | No | Explicit Spark session used to read metadata. |

## Returns

Deterministic source, contract, column, enrichment, freshness, and Guardrail context.

## Raises / Errors

Raises for missing or conflicting Production Catalogue and active Data Contract records.

## Notes

<div class="reference-docstring-notes" markdown="1">

This Preview function reads ``METADATA_DATA_CATALOGUE`` and the active frozen
``METADATA_DATA_CONTRACT`` in the configured Metadata Lakehouse. It does not
call AI or persist a second copy of the governed metadata.

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

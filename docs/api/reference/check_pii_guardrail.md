# `check_pii_guardrail`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview reference-lifecycle-chip-prominent">Preview</span>
<span class="reference-chip reference-chip-muted">Public function</span>
</p>

> This function is available for evaluation but is not part of the supported Live release contract. It may change without backward-compatibility guarantees.

Require Direct PII to be absent or represented by an approved token-vault token.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/pipeline/check_pii_guardrail.py:25`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline/check_pii_guardrail.py#L25-L153">View on GitHub</a>
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
def check_pii_guardrail(table_id: str, *, dataframe=None) -> dict
```

</div>

## Example usage

<div class="reference-example-usage" markdown="1">

>>> result = check_pii_guardrail("lakehouse:source:dbo:customers")
>>> result["can_continue"]
True

</div>

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `table_id` | `str` | Yes | Canonical identity of an active registered Catalogue table. |
| `dataframe` | `DataFrame` | No | Incoming DataFrame to check. When omitted, FabricOps reads the configured physical table without silently detokenising it. |

## Returns

Structured PII guardrail status, continuation decision, and classified, present, and untreated columns.

## Raises / Errors

ValueError
    If the registered table or configured store is unsupported.
SchemaDriftError
    If a blocking PII Guardrail rejects untreated Direct PII.

## Notes

<div class="reference-docstring-notes" markdown="1">

Development uses mutable ``METADATA_ENRICHMENT`` classification. Production
uses the active frozen Data Contract enrichment. Approved tokens are checked
against the separately configured, table-isolated ``pii_token_vault`` target;
reversible mappings never enter ordinary governance metadata.

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

# `check_guardrail_coverage`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview reference-lifecycle-chip-prominent">Preview</span>
<span class="reference-chip reference-chip-muted">Public function</span>
</p>

> This function is available for evaluation but is not part of the supported Live release contract. It may change without backward-compatibility guarantees.

Verify that every governed pipeline participant and configured Guardrail is ready before publication.

<div class="reference-docstring-intro" markdown="1">

Development may still perform a contract-free baseline run so Engineering
can populate Catalogue and Profile metadata before Governance authors the
first Data Contracts. Once any Data Contract is selected, every participating
source and target must have a selected contract with at least one active
Guardrail that applies to its pipeline role. Every applicable configured
Guardrail must also have current-activity evidence before publication.

FabricOps does not require a fixed Guardrail bundle. Governance can choose
the Guardrails appropriate to each table; Schema is a common minimal choice.

</div>

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/pipeline/check_guardrail_coverage.py:83`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline/check_guardrail_coverage.py#L83-L287">View on GitHub</a>
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
def check_guardrail_coverage(
    target_table_id: str,
    source_table_ids: list[str] | tuple[str, ...],
    verbose: bool=True,
) -> dict[str, Any]:
```

</div>

## Example usage

<div class="reference-example-usage" markdown="1">

```python
coverage = check_guardrail_coverage(target_table_id=target_table_id, source_table_ids=source_table_ids)
```

</div>

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `target_table_id` | `str` | Yes | Not documented yet |
| `source_table_ids` | `list[str] \| tuple[str, ...]` | Yes | Not documented yet |
| `verbose` | `bool` | No | Not documented yet |

## Returns

Readiness, evaluated coverage, missing evaluations, issues, and the publication continuation decision.

### Return interpretation

can_continue is true only when contract readiness and current-activity Guardrail coverage permit publication; Development can explicitly skip a contract-free baseline run.

## Raises / Errors

Raises ValueError for missing canonical identities or missing Fabric activity identity.

### Common failure causes

- A participating table has no selected Data Contract.
- A selected contract has no applicable active Guardrail.
- An applicable Guardrail has no result for the current activity.
- The current Fabric activity identity is unavailable.

## See also

- [Pipeline Execution](../../guided-demo/02-run-pipeline.md)


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

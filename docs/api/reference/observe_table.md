# `observe_table`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview reference-lifecycle-chip-prominent">Preview</span>
<span class="reference-chip reference-chip-muted">Public function</span>
</p>

> This function is available for evaluation but is not part of the supported Live release contract. It may change without backward-compatibility guarantees.

Persist deterministic partition evidence for one physical source table.

<div class="reference-docstring-intro" markdown="1">

This internal helper records row count, earliest/latest change values, and
a deterministic content fingerprint by source partition.

</div>

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/pipeline/observe_table.py:156`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline/observe_table.py#L156-L285">View on GitHub</a>
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
def observe_table(
    table_name: str,
    target: str='source',
    schema: str | None=None,
) -> Any:
```

</div>

## Example usage

<div class="reference-example-usage" markdown="1">

```python
observation = observe_table("orders", target="source", schema="dbo")
```

</div>

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `table_name` | `str` | Yes | Table name within the configured target. |
| `target` | `str` | No | Logical Lakehouse or Warehouse target configured by ``00_env_config``. |
| `schema` | `str \| None` | No | Optional Lakehouse schema. A schema is required for Warehouse targets. |

## Returns

Canonical METADATA_SOURCE_OBSERVATION rows for the current activity.

## Raises / Errors

ValueError
    If table identity, target type, or a required active Source Stability rule
    is invalid.
RuntimeError
    If ``00_env_config`` has not initialized FabricOps or observation
    cannot be collected or persisted.

## Notes

<div class="reference-docstring-notes" markdown="1">

The stored evidence includes a stable ``observation_id``, partition values,
counts, observed change-value range, and a deterministic fingerprint over
business content. Warehouse aggregation is pushed into SQL and Lakehouse
aggregation remains distributed; full business rows are not persisted in
metadata.

Evidence is appended only after collection succeeds. This function neither
loads history nor makes guardrail decisions; ``check_source_stability`` owns
comparison and removal tombstones. The stable ``table_id`` is built from the
resolved physical identity with the same logical identity rules used by
:func:`profile_and_register_table`. It is independent of Development or
Production; ``environment_name`` keeps those operational observations
separate without requiring a pre-existing catalogue row.

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

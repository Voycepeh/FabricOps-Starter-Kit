# `write_pipeline_prep`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview reference-lifecycle-chip-prominent">Preview</span>
<span class="reference-chip reference-chip-muted">Public function</span>
</p>

> This function is available for evaluation but is not part of the supported Live release contract. It may change without backward-compatibility guarantees.

Prepare governed target write inputs and technical fields without physically writing.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/pipeline/write_pipeline_prep.py:68`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline/write_pipeline_prep.py#L68-L232">View on GitHub</a>
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
def write_pipeline_prep(
    df,
    target_table_id: str | None=None,
    target: str | None=None,
    schema: str | None=None,
    table_name: str | None=None,
    load_strategy: str | None=None,
    load_strategy_parameters: dict[str, Any] | None=None,
    source_preps: list[dict[str, Any]],
) -> dict[str, Any]:
```

</div>

## Example usage

<div class="reference-example-usage" markdown="1">

>>> write_prep = write_pipeline_prep(
...     transformed_df,
...     target_table_id="lakehouse:unified:dbo:students",
...     source_preps=[read_prep],
... )
>>> write_prep["mode"]
'append'

</div>

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `df` | `pyspark.sql.DataFrame` | Yes | Business target DataFrame after target schema and DQ checks pass. |
| `target_table_id` | `str \| None` | No | Canonical registered target identity used to resolve physical target metadata. A selected or active frozen Data Contract is authoritative for its load strategy, parameters, and owning logical notebook name. |
| `target` | `str \| None` | No | Configured target key supplied instead of ``target_table_id``. |
| `schema` | `str \| None` | No | Physical target schema, when the configured store uses schemas. |
| `table_name` | `str \| None` | No | Physical target table name. Required with ``target`` when ``target_table_id`` is omitted. |
| `load_strategy` | `str \| None` | No | Current authored load strategy when physical identity is supplied. |
| `load_strategy_parameters` | `dict[str, Any] \| None` | No | Parameters belonging to the authored load strategy. |
| `source_preps` | `list[dict[str, Any]]` | Yes | Results returned by :func:`read_pipeline_prep` for the sources that fed this target. |

## Returns

Audited DataFrame, target identity, authoritative load strategy, writer settings, write scope, and post-write success context.

## Raises / Errors

ValueError
    If preparation is incomplete or an unsafe target/strategy combination
    is requested, or if a contract-backed target is invoked by a notebook
    other than its frozen owner.

## Notes

<div class="reference-docstring-notes" markdown="1">

FabricOps resolves one run-level audit record and adds only compact target
provenance fields. This function does not call a Lakehouse or Warehouse
writer. It does not persist successful target Lineage or Source Consumption;
the physical writer commits those records only after publication succeeds.
Lakehouse and Warehouse targets use the same governed target strategy
definition; each writer applies its engine-specific physical execution only
after this preparation succeeds. One governed target ``table_id`` must have
one owning pipeline/notebook writer because independent writers can race,
duplicate writes, overwrite state, or break SCD history.

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

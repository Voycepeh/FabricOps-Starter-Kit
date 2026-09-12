# `pipeline_write`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview reference-lifecycle-chip-prominent">Preview</span>
<span class="reference-chip reference-chip-muted">Public function</span>
</p>

> This function is available for evaluation but is not part of the supported Live release contract. It may change without backward-compatibility guarantees.

Publish one governed pipeline target through its configured Fabric store.

<div class="reference-docstring-intro" markdown="1">

``pipeline_write`` is the governed pipeline-orchestration equivalent of
:func:`write_lakehouse_table` and :func:`write_warehouse_table`. Describe
the governed target once; FabricOps resolves its canonical identity and
configured store, resolves governed processing from the selected or active
Data Contract, selects the appropriate physical publication path, and
commits pipeline-success metadata only after publication succeeds.

</div>

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/pipeline/pipeline_write.py:62`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline/pipeline_write.py#L62-L331">View on GitHub</a>
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
def pipeline_write(
    df,
    target: str | None=None,
    schema: str | None=None,
    table_name: str | None=None,
    table_id: str | None=None,
    load_strategy: str | None=None,
    load_strategy_parameters: dict[str, Any] | None=None,
    repartition_by=None,
    options: dict[str, Any] | None=None,
) -> dict[str, str]:
```

</div>

## Example usage

<div class="reference-example-usage" markdown="1">

Publish without knowing whether ``unified`` is a Lakehouse or Warehouse:

>>> result = pipeline_write(
...     prepared_df, target="unified", schema="demo",
...     table_name="curated_orders",
... )
>>> result["table_id"]
'lakehouse:unified:demo:curated_orders'

Development may propose processing, without bypassing contract authority:

>>> pipeline_write(
...     prepared_df, target="unified", schema="demo",
...     table_name="curated_orders", load_strategy="overwrite",
... )

</div>

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `df` | `pyspark.sql.DataFrame` | Yes | Prepared target DataFrame after explicit target checks have passed. |
| `target` | `str \| None` | No | Configured target key. Supply it with ``table_name`` and optional ``schema`` instead of ``table_id``. |
| `schema` | `str \| None` | No | Physical target schema when the configured store uses schemas. |
| `table_name` | `str \| None` | No | Physical target table name. Required with ``target`` when ``table_id`` is omitted. |
| `table_id` | `str \| None` | No | Canonical registered target identity. This identity form is mutually exclusive with ``target``, ``schema``, and ``table_name``. |
| `load_strategy` | `str \| None` | No | Development-authored processing proposal. Selected or frozen contract validation applies in Development, and the active approved Data Contract remains authoritative in Production. |
| `load_strategy_parameters` | `dict[str, Any] \| None` | No | Development-authored strategy parameters, such as key, effective, tracked, or partition columns, subject to contract validation. |
| `repartition_by` | `int or str or list[str] or tuple[str, ...]` | No | Optional Spark repartitioning passed to simple physical writes. |
| `options` | `dict[str, Any] \| None` | No | Additional physical writer options for append or overwrite publication. |

## Returns

A small result containing the canonical target table_id.

## Raises / Errors

ValueError
    If identity inputs conflict or are incomplete, no source was registered
    by ``pipeline_read`` for the current activity, governed processing is
    invalid, ownership does not match, or the target store is unsupported.

## Notes

<div class="reference-docstring-notes" markdown="1">

The governed orchestration performs these mechanical steps:

1. Resolve the canonical target ``table_id``.
2. Resolve the configured physical target identity.
3. Resolve the selected or active Data Contract.
4. Resolve the governed load strategy and parameters.
5. Resolve processing scope.
6. Apply FabricOps target audit fields.
7. Validate target notebook ownership.
8. Select the physical Lakehouse or Warehouse publication implementation.
9. Perform append/overwrite or dedicated SCD processing.
10. Only after physical success, commit target Lineage and accepted Source
    Observation/write-success metadata.
11. Establish target profile-registration context.
12. Return a small publication result.

Callers do not provide a store type, manually resolve ``table_id``, choose
a Lakehouse versus Warehouse writer, construct processing scope or success
context, or manually commit Lineage or Source Observation metadata. Source
identities are recovered from successful ``pipeline_read`` calls registered
for the current activity. Multiple source reads can feed one target.

This function does not perform transformations, schema checks, DQ checks,
Sensitive Data Guardrails, or profiling. Those remain explicit notebook
engineering and governance steps. ``pipeline_write`` publishes governed
table targets only. Raw Lakehouse Files do not have a canonical FabricOps
``table_id``; direct file-output concerns, if supported in future, belong
outside this governed table orchestration API.

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

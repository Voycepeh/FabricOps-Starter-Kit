# `profile_and_register_table`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview reference-lifecycle-chip-prominent">Preview</span>
<span class="reference-chip reference-chip-muted">Public function</span>
</p>

> This function is available for evaluation but is not part of the supported Live release contract. It may change without backward-compatibility guarantees.

Profile a Spark DataFrame, save a profiling snapshot, update catalogue records, and record source or target activity.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/pipeline/profile_and_register_table.py:466`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline/profile_and_register_table.py#L466-L636">View on GitHub</a>
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
def profile_and_register_table(
    df,
    profile_role,
    target,
    table_name,
    schema=None,
    frequency_columns=None,
    frequency_top_n: int | None=None,
    frequency_max_distinct_percent: float | None=80.0,
    frequency_profile_df=None,
):
```

</div>

## Example usage

<div class="reference-example-usage" markdown="1">

>>> result = profile_and_register_table(
...     source_df,
...     profile_role="source",
...     target="raw",
...     table_name="customers",
...     frequency_columns=["status"],
... )
>>> "frequency_json" in result.columns
False

</div>

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `df` | `pyspark.sql.DataFrame` | Yes | Complete Spark DataFrame to profile. |
| `profile_role` | `{"source", "target"}` | Yes | Lineage role recorded for the profiled asset. |
| `target` | `str` | Yes | Configured Fabric store key containing the asset. |
| `table_name` | `str` | Yes | Physical table name represented by ``df``. |
| `schema` | `str` | No | Physical schema name, or the configured default when omitted. |
| `frequency_columns` | `sequence of str` | No | Columns whose flattened value distributions should be persisted. ``None`` automatically selects eligible scalar columns and an empty sequence disables frequency profiling. |
| `frequency_top_n` | `int \| None` | No | Maximum ranked values persisted per selected column. ``None`` keeps all. |
| `frequency_max_distinct_percent` | `float \| None` | No | Maximum distinct-per-non-null percentage for automatic selection. ``None`` disables this automatic cardinality threshold. |
| `frequency_profile_df` | `pyspark.sql.DataFrame` | No | Alternate DataFrame used only by ``profile_frequency_distribution``. |

## Returns

Spark DataFrame containing one compact profiling summary row for each eligible column appended to METADATA_DATA_PROFILED, including stable identities, complete-DataFrame statistics, schema fingerprint, profiling timestamp, and runtime audit fields.

### Return interpretation

The returned rows are the compact parent summaries. Flattened frequency rows are written separately to METADATA_DATA_PROFILED_FREQUENCY and join to the returned rows through metadata_column_key; frequency, catalogue, and lineage rows are side effects and are not returned.

## Raises / Errors

Raises ValueError for an unsupported profile_role, unknown target, unsupported configured store kind, or invalid table or schema identity.

### Common failure causes

- profile_role must be source or target, or the configured target store kind is unsupported.
- target or table_name is blank, or a schema-enabled store has no explicit or configured schema.
- frequency_profile_df is not Spark DataFrame-like, uses an incompatible Spark session, or is missing selected frequency columns.
- The configured metadata target cannot be resolved or written.
- Requested frequency columns are missing or expensive to group; frequency_top_n limits returned values only and does not reduce grouping cost.
- If lineage registration fails after profile and catalogue writes succeed, RuntimeError is raised and earlier writes remain completed.

## Notes

<div class="reference-docstring-notes" markdown="1">

``METADATA_DATA_PROFILED`` stores one compact statistical summary per
profiled column. ``profile_frequency_distribution`` creates normalized
frequency output, which this function writes as one row per distinct value
to ``METADATA_DATA_PROFILED_FREQUENCY``. The tables join through
``metadata_column_key`` and parent and child rows share ``profiled_at``.
Temporary ``COLUMN_NAME`` and ``DATA_TYPE`` fields resolve the stable parent
identity but are not persisted in the child table. Existing child rows for
the profiled column keys are replaced so obsolete values cannot survive a
later execution. Catalogue and lineage writes retain their existing roles.

This is a breaking physical-schema contract: metadata tables created with
``frequency_json`` in ``METADATA_DATA_PROFILED`` must be recreated through
the established metadata setup flow. No compatibility or migration layer is
provided. All writes route through the metadata lakehouse configured by
``00_env_config``.

</div>

## See also

- [Pipeline Execution](../../guided-demo/run-pipeline.md)


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

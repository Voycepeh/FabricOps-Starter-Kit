# `profile_and_register_dataframe`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview reference-lifecycle-chip-prominent">Preview</span>
<span class="reference-chip reference-chip-muted">Public function</span>
</p>

> This function is available for evaluation but is not part of the supported Live release contract. It may change without backward-compatibility guarantees.

## Call-flow summary

- Downstream callables: 138
- Shared helpers: 52
- Private helpers: 84

<a class="reference-source-link" href="../../../assets/public-function-call-flows-dashboard.html?function=profile_and_register_dataframe">Open Preview call flow</a>

Profile detailed evidence to METADATA_DATA_PROFILED and upsert catalogue identities to METADATA_DATA_CATALOGUE.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/pipeline/profile_and_register_dataframe.py:330`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline/profile_and_register_dataframe.py#L330-L452">View on GitHub</a>
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
def profile_and_register_dataframe(
    df,
    profile_role,
    environment_name,
    store_type,
    layer,
    table_name,
    schema_name=None,
    frequency_columns=None,
    frequency_top_n=20,
    is_sampled=False,
):
```

</div>

## Example usage

<div class="reference-example-usage" markdown="1">

```python
profiled_df = profile_and_register_dataframe(df_customer, profile_role="source", environment_name=ENVIRONMENT_NAME, store_type="lakehouse", layer="raw", table_name="customer")
```

</div>

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `df` | `pyspark.sql.DataFrame` | Yes | Spark DataFrame to profile exactly as supplied by the caller. The helper does not sample, re-read, or mutate this DataFrame. |
| `profile_role` | `{"source", "target"}` | Yes | Execution participation context for the DataFrame in the notebook flow. The validated value is not stored in ``METADATA_DATA_PROFILED`` or ``METADATA_DATA_CATALOGUE``; an automatic lineage flow records one table-level runtime participation row. |
| `environment_name` | `str` | Yes | FabricOps environment name to persist with the catalogue snapshot. |
| `store_type` | `{"lakehouse", "warehouse"}` | Yes | Physical store type for the profiled asset. |
| `layer` | `str` | Yes | Logical lakehouse or warehouse layer for the profiled asset. |
| `table_name` | `str` | Yes | Physical table name for the profiled asset. |
| `schema_name` | `str` | No | Optional physical schema name. Use ``None`` for lakehouse tables without a separate schema. |
| `frequency_columns` | `sequence of str` | No | Columns to pass to ``profile_frequency_distribution`` for top-N value evidence. ``None`` or an empty sequence skips frequency profiling. |
| `frequency_top_n` | `int, default=20` | No | Number of ranked values to request from frequency profiling. |
| `is_sampled` | `bool, default=False` | No | Caller-declared provenance flag persisted in the profiled evidence. |

## Returns

Detailed Spark DataFrame appended to METADATA_DATA_PROFILED.

### Return interpretation

The returned rows are exactly the catalogue snapshot submitted to the metadata writer for the supplied DataFrame.

## Raises / Errors

Raises ValueError for unsupported profile_role, unsupported store_type, or empty required identity fields; lower-level profiling validation is preserved.

### Common failure causes

- 00_env_config has not been run.
- profile_role or store_type is unsupported.
- Required physical identity inputs are blank.
- Requested frequency columns are missing from the DataFrame.

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

!!! info "Generated reference freshness"
    Reference pages generated: 14 Jul 2026, 9:35 PM SGT
    Call-flow data generated: 14 Jul 2026, 9:32 PM SGT

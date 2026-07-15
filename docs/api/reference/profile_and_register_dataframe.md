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

<div class="reference-docstring-intro" markdown="1">

The function profiles the supplied DataFrame exactly as provided by the
caller, then registers column-level statistics, optional top-value
frequencies, physical catalogue identities, and one table-level runtime
lineage participation event in the configured FabricOps metadata lakehouse.
The original business DataFrame is not written by this function, and the
function does not sample, re-read, or mutate the supplied DataFrame. All
metadata writes are routed to the configured ``metadata`` target resolved
from ``00_env_config``.

</div>

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/pipeline/profile_and_register_dataframe.py:330`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline/profile_and_register_dataframe.py#L330-L573">View on GitHub</a>
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
| `profile_role` | `{"source", "target"}` | Yes | Records whether the profiled asset participated in the notebook activity as an input or an output: ``source`` for an activity input and ``target`` for an activity output. The value is stored in ``METADATA_DATA_LINEAGE`` rather than in ``METADATA_DATA_PROFILED`` or ``METADATA_DATA_CATALOGUE``. |
| `environment_name` | `str` | Yes | FabricOps environment context used to resolve the metadata target configuration and persisted environment identity. |
| `store_type` | `{"lakehouse", "warehouse"}` | Yes | Physical store type of the business asset being profiled. This identifies the asset and does not redirect metadata writes to that business store. |
| `layer` | `str` | Yes | Logical lakehouse or warehouse layer of the business asset being profiled. This identifies the asset and does not redirect metadata writes. |
| `table_name` | `str` | Yes | Physical table name of the business asset being profiled. This identifies the asset and does not redirect metadata writes. |
| `schema_name` | `str` | No | Optional physical schema name for the business asset. Use ``None`` for lakehouse tables without a separate schema. This identifies the asset and does not redirect metadata writes. |
| `frequency_columns` | `sequence of str` | No | Selected columns that should receive embedded top-value frequency evidence. ``None`` or an empty sequence skips frequency profiling entirely. Requested columns should also be eligible for the main statistical profile. |
| `frequency_top_n` | `int, default=20` | No | Number of ranked values to retain per selected frequency column. |
| `is_sampled` | `bool, default=False` | No | Caller-declared provenance flag persisted in the profiled evidence only. It does not cause sampling. When ``True``, the supplied DataFrame must already have been sampled by the caller, and all counts and percentages describe that supplied sample. |

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

## Notes

<div class="reference-docstring-notes" markdown="1">

Processing flow:

1. Run ``profile_dataframe(df)`` to produce one statistical profile row per
   eligible input column.
2. When ``frequency_columns`` is provided, run
   ``profile_frequency_distribution`` over those columns using
   ``frequency_top_n``.
3. Convert the multiple frequency rows for each column into one
   deterministic JSON document.
4. Left-join that JSON to the statistical profile on
   ``profile_dataframe.COLUMN_NAME = profile_frequency_distribution.COLUMN_NAME``.
5. Append the detailed profile rows to ``METADATA_DATA_PROFILED``.
6. Derive and upsert physical column identities into
   ``METADATA_DATA_CATALOGUE``.
7. Upsert one table-level source or target participation event into
   ``METADATA_DATA_LINEAGE``.
8. Return the detailed Spark DataFrame written to
   ``METADATA_DATA_PROFILED``.

Frequency join behavior:

- The statistical profile is the left side of the join, so every eligible
  statistical profile row remains in the returned result.
- Only columns listed in ``frequency_columns`` receive ``frequency_json``.
  Other profiled columns receive null for ``frequency_json``.
- ``frequency_columns=None`` or an empty sequence skips frequency profiling
  entirely.
- Frequency values are ordered deterministically by rank.

Example ``frequency_json`` structure:

.. code-block:: json

   {
     "profiled_row_count": 1000,
     "profiled_non_null_count": 995,
     "values": [
       {
         "value": "Active",
         "count": 700,
         "percent": 70.0,
         "rank": 1
       }
     ]
   }

``METADATA_DATA_PROFILED`` receives one appended row per eligible input
DataFrame column. Repeated executions create additional profiling
snapshots, and the returned DataFrame is the same detailed DataFrame
appended to this table. Its logical field groups are:

- Identity fields: ``metadata_table_key``, ``metadata_column_key``,
  ``environment_name``, ``store_type``, ``layer``, ``schema_name``,
  ``table_name``, ``column_name``, ``data_type``.
- Statistical fields: ``row_count``, ``non_null_count``, ``null_count``,
  ``null_percent``, ``distinct_count``, ``distinct_percent``,
  ``mean_value``, ``stddev_value``, ``min_value``,
  ``percentile_25_value``, ``median_value``, ``percentile_75_value``,
  ``max_value``.
- Frequency and provenance fields: ``is_sampled``, ``frequency_json``,
  ``schema_fingerprint``, ``profiled_at``.
- Audit fields: ``_committed_by``, ``_committed_at``, ``_workspace_id``,
  ``_workspace_name``, ``_notebook_id``, ``_notebook_name``,
  ``_metadata_lakehouse_name``, ``_activity_id``.

``metadata_table_key`` is a deterministic identity derived from
environment, store type, layer, schema, and table name.
``metadata_column_key`` is derived from the table key and column name.
``schema_fingerprint`` identifies the observed Spark schema.

``METADATA_DATA_CATALOGUE`` stores physical table and column identities,
not profiling measurements. The function derives catalogue rows from the
detailed profile and upserts ``metadata_table_key``,
``metadata_column_key``, ``schema_fingerprint``, ``environment_name``,
``store_type``, ``layer``, ``schema_name``, ``table_name``,
``column_name``, ``data_type``, and the standard audit fields using
``metadata_table_key + metadata_column_key + schema_fingerprint`` as the
idempotent identity. Reprofiling the same column under the same schema
updates the existing identity, while a changed schema fingerprint can
create a new catalogue snapshot.

``METADATA_DATA_LINEAGE`` stores one table-level lineage participation row
per function call. Key lineage fields include ``lineage_event_id``,
``activity_id``, ``notebook_id``, ``notebook_name``, ``workspace_id``,
``workspace_name``, ``metadata_table_key``, ``schema_fingerprint``,
``profile_role``, ``profiled_at``, ``committed_by``,
``environment_name``, ``metadata_lakehouse_name``, and the standard audit
fields. ``lineage_event_id`` is deterministically derived from
``activity_id``, ``metadata_table_key``, ``schema_fingerprint``, and
``profile_role``.

Profile and catalogue registration occur before lineage registration. If
lineage registration fails after those writes succeed, the function raises
a ``RuntimeError`` explaining that profile and catalogue registration
succeeded but lineage registration failed. Guardrail execution is a
separate workflow.

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

!!! info "Generated reference freshness"
    Reference pages generated: 15 Jul 2026, 2:26 PM SGT
    Call-flow data generated: 14 Jul 2026, 9:32 PM SGT

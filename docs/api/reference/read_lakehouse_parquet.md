# `read_lakehouse_parquet`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-live reference-lifecycle-chip-prominent">Live</span>
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-live reference-lifecycle-chip-prominent">Live since 0.1.0</span>
<span class="reference-chip reference-chip-muted">Public function</span>
</p>

> This function is part of the supported FabricOps public contract. Changes to its signature, behaviour, public export, or Live-critical dependencies require Live-contract review.

Read a Parquet path from a configured Fabric-resolved path through Spark Parquet.

<div class="reference-docstring-intro" markdown="1">

Use ``read_lakehouse_parquet`` for Parquet files stored under the
Lakehouse ``Files`` area. Use ``read_lakehouse_table`` for managed Delta
tables stored under the Lakehouse ``Tables`` area.

This function reads from the Lakehouse ``Files`` area, not a managed Delta
table in the ``Tables`` area. FabricOps resolves the logical target and
relative path through configuration, attempts a normal Spark Parquet read
first, forces a small Spark action to verify that the data can actually be
decoded, falls back to a derived ``_tsus`` path when the original read
fails, may create a converted Parquet copy with microsecond timestamp
precision when the fallback path is missing, and returns a Spark DataFrame
backed by either the original path or the fallback path.

</div>

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/io/read_lakehouse_parquet.py:15`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/read_lakehouse_parquet.py#L15-L210">View on GitHub</a>
</div>

<p class="reference-catalogue-item-meta reference-catalogue-item-badges">
<span class="reference-chip">Public Starter Kit function</span>
<span class="reference-chip">99_explore</span>
</p>

**Used in notebooks:** `99_explore`

## Usage notes

These IO helpers exist because Fabric notebooks can only attach to one lakehouse or warehouse at a time. Use them when a notebook needs a supported and repeatable way to read from or write to the configured Fabric store.

They keep IO behavior consistent across Starter Kit notebooks and avoid ad hoc connection logic.


## Signature

<div class="reference-api-definition" markdown="1">

```python
def read_lakehouse_parquet(
    relative_path: str,
    target: str='source',
    verbose: bool=True,
    spark_session=None,
    context: dict[str, Any] | None=None,
    **options,
):
```

</div>

## Example usage

<div class="reference-example-usage" markdown="1">

```python
source_df = read_lakehouse_parquet("Files/curated/student_enrolment/", target="source", spark_session=spark)
```

</div>

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `relative_path` | `str` | Yes | Parquet file path resolved underneath the configured Lakehouse ``Files`` area. Root-level files such as ``customers.parquet`` and nested paths such as ``incoming/2026/customers.parquet`` are supported. |
| `target` | `str` | No | Logical Lakehouse target from ``00_env_config``. |
| `verbose` | `bool` | No | Whether to print operational progress for original path attempts, original read success or failure, ``_tsus`` path attempts, conversion attempts, and fallback success or failure. It does not change the resulting data. |
| `spark_session` | `object` | No | Spark session to use instead of the notebook global ``spark``. |
| `context` | `dict[str, Any] \| None` | No | Active Fabric context override. **options Additional Spark Parquet reader options forwarded to Spark's Parquet reader for the original path read, the existing ``_tsus`` path read, and the read after conversion. Representative options include ``mergeSchema``, ``recursiveFileLookup``, ``pathGlobFilter``, ``modifiedBefore``, and ``modifiedAfter``. FabricOps does not interpret these options. |

## Returns

Spark DataFrame backed by the selected Parquet file or folder. One DataFrame row represents one source record; partition columns may be added by Spark when reading partitioned folders.

### Return interpretation

The function verifies decodability with a one-row Spark action before returning, then downstream transformations remain normal Spark DataFrame operations.

## Raises / Errors

Raises ValueError for invalid relative paths and Spark/read errors when the Parquet path cannot be loaded.

### Common failure causes

- The path is missing, inaccessible, empty, corrupt, or not Parquet.
- Schemas are incompatible across files unless Spark options such as mergeSchema are appropriate.
- Schema merging can be expensive on large partitioned folders.
- The configured target cannot be resolved or read.
- Failures can occur during the initial validation action or later Spark evaluation.

## Notes

<div class="reference-docstring-notes" markdown="1">

Normal read flow:

``Configured Lakehouse Files path -> Spark Parquet read -> df.limit(1).collect() -> Return DataFrame when decoding succeeds``

Spark reads are normally lazy, but this function deliberately executes
``limit(1).collect()`` before returning. The validation action confirms
that Spark can decode at least one row. The function is therefore not a
purely lazy reader, but it does not collect the entire dataset to the
driver.

``target`` is a logical Lakehouse target from ``00_env_config`` and
``relative_path`` is resolved under the configured Lakehouse ``Files``
area. Root-level and nested paths are supported. The resolved location is
conceptually ``<configured lakehouse>/Files/<relative_path>``. Examples:

``df = read_lakehouse_parquet("customers.parquet", target="source")``

``df = read_lakehouse_parquet("incoming/2026/customers.parquet", target="source")``

Derived ``_tsus`` fallback naming:

- ``customers.parquet`` becomes ``customers_tsus.parquet``.
- ``incoming/2026/customers.parquet`` becomes
  ``incoming/2026_tsus/customers.parquet``.

The function does not replace the original file.

The fallback begins after any exception from the original Spark read or
validation action. The current implementation does not first confirm that
the original failure is definitely timestamp-related. It then attempts the
``_tsus`` path. If that path is missing, it performs one single-file
conversion and retries. If both original and fallback reads fail, the
function raises ``RuntimeError``. Underlying Spark, pandas, PyArrow, path,
mount, or conversion errors may appear in verbose output before the final
``RuntimeError``.

The compatibility copy is produced by reading the original Parquet file
with pandas and PyArrow, then rewriting it as a new Parquet file using
microsecond timestamp precision with ``coerce_timestamps="us"`` and
truncated timestamps allowed. The compatibility copy may lose
sub-microsecond timestamp precision because nanosecond timestamps are
coerced to microseconds.

Spark may normally read a Parquet file or compatible dataset path, but the
automatic conversion helper is designed for one local Parquet file. It is
not a distributed folder conversion workflow, and large or multi-file
remediation should be handled as a separate conversion pipeline.

The normal Spark read uses the resolved configured ABFSS path. The
conversion fallback assumes the file is also accessible through the
notebook's default attached Lakehouse mount under
``/lakehouse/default/Files/``. A configured target may resolve correctly
for Spark reading while still being unavailable to the local fallback
mount, in which case fallback conversion can fail.

Compact reader-option example:

``df = read_lakehouse_parquet("incoming/events.parquet", target="source", mergeSchema=True)``

This function does not read a managed Delta table, register Parquet data as
a Lakehouse table, replace or modify the original Parquet file, convert
every file in a Parquet folder, perform a distributed timestamp
conversion, guarantee that the original failure was timestamp-related,
preserve nanosecond precision in the converted copy, delete or refresh an
existing ``_tsus`` copy, register metadata, profile the returned
DataFrame, or automatically cache or persist the returned DataFrame.

</div>

## See also

- [Templates](../../notebook-templates.md)


<details>
<summary>Maintainer architecture details</summary>

## Contract impact

| Property | Value |
| --- | --- |
| Lifecycle | <span class="reference-chip reference-lifecycle-chip reference-lifecycle-live">Live</span> |
| Live since | 0.1.0 |
| Discontinued in | — |
| Contract classification | Live public function |
| Contract risk | Live |
| Live-critical dependencies | 14 |

### Release history

| Status | Version |
| --- | --- |
| Live | 0.1.0 |

### Live-critical dependencies

<ul class="reference-compact-list">
<li><code>fabricops_kit.config.shared._normalize_path_config</code></li>
<li><code>fabricops_kit.config.shared.get_default_fabric_context</code></li>
<li><code>fabricops_kit.config.shared.get_store</code></li>
<li><code>fabricops_kit.config.shared.resolve_fabric_context</code></li>
<li><code>fabricops_kit.io.shared._join_lakehouse_area_path</code></li>
<li><code>fabricops_kit.io.shared._validate_lakehouse_store</code></li>
<li><code>fabricops_kit.io.shared._validate_relative_path</code></li>
<li><code>fabricops_kit.io.shared._validate_warehouse_store</code></li>
<li><code>fabricops_kit.io.shared.convert_single_parquet_ns_to_us</code></li>
<li><code>fabricops_kit.io.shared.get_spark_session</code></li>
<li><code>fabricops_kit.io.shared.resolve_configured_file_path</code></li>
<li><code>fabricops_kit.io.shared.resolve_lakehouse_file_location</code></li>
<li><code>fabricops_kit.io.shared.resolve_lakehouse_file_path</code></li>
<li><code>fabricops_kit.io.shared.resolve_target_store</code></li>
</ul>


</details>

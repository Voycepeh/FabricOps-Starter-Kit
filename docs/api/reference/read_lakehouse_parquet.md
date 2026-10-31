# `read_lakehouse_parquet`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-live reference-lifecycle-chip-prominent">Live</span>
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-live reference-lifecycle-chip-prominent">Live since 0.1.0</span>
</p>

> This function is part of the supported FabricOps public contract. Changes to its signature, behaviour, public export, or Live-critical dependencies require Live-contract review.

Read a Parquet path from a configured Fabric-resolved path through Spark Parquet.

<p class="reference-catalogue-item-meta reference-catalogue-item-badges">
<span class="reference-chip">00C_demo_setup</span>
</p>

## Usage notes

Use when reading a Parquet file or path from a configured Fabric lakehouse Files path.


## Example usage

<div class="reference-example-usage" markdown="1">

```python
orders_df = read_lakehouse_parquet("curated/orders/")
```

</div>

<details class="reference-signature-details" markdown="1">
<summary>Signature</summary>

## Signature

<div class="reference-api-definition" markdown="1">

```python
def read_lakehouse_parquet(
    relative_path: str,
    *,
    store: str='Bronze',
    verbose: bool=True,
    context: dict[str, Any] | None=None,
    **options,
):
```

</div>

</details>

## Parameters

Required describes the Python signature. An optional parameter may still be needed for the selected mode or identity form; see its description. `—` means no signature default.

<div class="reference-input-table" markdown="1">

| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `relative_path` | `str` | Yes | `—` | Parquet file path resolved underneath the configured Lakehouse ``Files`` area. Root-level files such as ``customers.parquet`` and nested paths such as ``incoming/2026/customers.parquet`` are supported. |
| `store` | `str` | No | `'Bronze'` | Logical Lakehouse store key from ``00_env_config``. |
| `verbose` | `bool` | No | `True` | Whether to print operational progress for original path attempts, original read success or failure, ``_tsus`` path attempts, conversion attempts, and fallback success or failure. It does not change the resulting data. |
| `context` | `dict[str, Any] \| None` | No | `None` | Active Fabric context override. |
| `**options` | `—` | No | `—` | Additional Spark Parquet reader options forwarded to Spark's Parquet reader for the original path read, the existing ``_tsus`` path read, and the read after conversion. Representative options include ``mergeSchema``, ``recursiveFileLookup``, ``pathGlobFilter``, ``modifiedBefore``, and ``modifiedAfter``. FabricOps does not interpret these options. |

</div>

## Returns

pyspark.sql.DataFrame
    A Spark DataFrame backed by either the original resolved Parquet path
    or the compatible ``_tsus`` fallback path. Before returning, the
    function executes a one-row Spark action to verify that the selected
    data can be decoded.

### Return interpretation

The function verifies decodability with a one-row Spark action before returning, then downstream transformations remain normal Spark DataFrame operations.

## Raises / Errors

RuntimeError
    When neither the original path nor the ``_tsus`` fallback path can be
    read successfully.

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

``store`` is a logical Lakehouse target from ``00_env_config`` and
``relative_path`` is resolved under the configured Lakehouse ``Files``
area. Root-level and nested paths are supported. The resolved location is
conceptually ``<configured lakehouse>/Files/<relative_path>``. Examples:

``df = read_lakehouse_parquet("customers.parquet", store="Bronze")``

``df = read_lakehouse_parquet("incoming/2026/customers.parquet", store="Bronze")``

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
``/lakehouse/default/Files/``. A configured store may resolve correctly
for Spark reading while still being unavailable to the local fallback
mount, in which case fallback conversion can fail.

Compact reader-option example:

``df = read_lakehouse_parquet("incoming/events.parquet", store="Bronze", mergeSchema=True)``

This function does not read a managed Delta table, register Parquet data as
a Lakehouse table, replace or modify the original Parquet file, convert
every file in a Parquet folder, perform a distributed timestamp
conversion, guarantee that the original failure was timestamp-related,
preserve nanosecond precision in the converted copy, delete or refresh an
existing ``_tsus`` copy, register metadata, profile the returned
DataFrame, or automatically cache or persist the returned DataFrame.

</div>

## Behavior and scope

<div class="reference-docstring-intro" markdown="1">

Spark is resolved automatically from the existing execution session.
No session is created; Spark-dependent work raises
``RuntimeError`` when no session is available.

Use ``read_lakehouse_parquet`` for Parquet files stored under the
Lakehouse ``Files`` area. Use ``read_lakehouse_table`` for managed Delta
tables stored under the Lakehouse ``Tables`` area.

This function reads from the Lakehouse ``Files`` area, not a managed Delta
table in the ``Tables`` area. FabricOps resolves the logical store key and
relative path through configuration, attempts a normal Spark Parquet read
first, forces a small Spark action to verify that the data can actually be
decoded, falls back to a derived ``_tsus`` path when the original read
fails, may create a converted Parquet copy with microsecond timestamp
precision when the fallback path is missing, and returns a Spark DataFrame
backed by either the original path or the fallback path.

</div>

## See also

- [Templates](https://github.com/Voycepeh/FabricOps-Starter-Kit/tree/main/templates/notebooks)

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/io/read_lakehouse_parquet.py:15`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/read_lakehouse_parquet.py#L15-L223">View on GitHub</a>
</div>


<details class="reference-implementation-details" markdown="1">
<summary>Maintainer architecture details</summary>

## Contract impact

| Property | Value |
| --- | --- |
| Lifecycle | <span class="reference-chip reference-lifecycle-chip reference-lifecycle-live">Live</span> |
| Live since | 0.1.0 |
| Discontinued in | — |
| Contract classification | Live public function |
| Contract risk | Live |
| Live-critical dependencies | 16 |

### Release history

| Status | Version |
| --- | --- |
| Live | 0.1.0 |
| Live | 0.2.0 |
| Live | 0.2.5 |
| Live | 0.3.0 |
| Live | 0.3.1 |

### Live-critical dependencies

<ul class="reference-compact-list">
<li><code>fabricops_kit.config.shared._get_fabric_runtime_context</code></li>
<li><code>fabricops_kit.config.shared._get_fabric_runtime_metadata</code></li>
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
<li><code>fabricops_kit.io.shared.resolve_store</code></li>
</ul>


</details>
